"""
Advanced AI Interview Simulator - Speech Processing Service
Whisper ASR integration + speech analytics (WPM, pauses, fillers, confidence).
"""
import io
import os
import re
import logging
import tempfile
from typing import Optional

import numpy as np

from config import settings

logger = logging.getLogger(__name__)

# ─── Filler words list ──────────────────────────────────────────────────
FILLER_WORDS = {
    "um", "uh", "er", "ah", "like", "you know", "basically",
    "actually", "literally", "right", "so", "well", "i mean",
    "sort of", "kind of", "you see", "okay so",
}


class SpeechProcessor:
    """
    Handles speech-to-text transcription and speech quality analytics.
    Uses OpenAI Whisper for ASR and librosa for audio feature extraction.
    """

    def __init__(self):
        self._whisper_model = None
        self._model_loaded = False

    def _load_whisper(self):
        """Lazy-load Whisper model to avoid slow startup."""
        if self._model_loaded:
            return
        try:
            import whisper
            logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
            self._whisper_model = whisper.load_model(settings.WHISPER_MODEL)
            self._model_loaded = True
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            raise RuntimeError(
                "Whisper model could not be loaded. "
                "Make sure 'openai-whisper' is installed: pip install openai-whisper"
            ) from e

    # ─── Transcription ────────────────────────────────────────────────

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.webm") -> dict:
        """
        Transcribe audio bytes to text using Whisper.
        Returns transcript + word-level timing segments.
        """
        self._load_whisper()

        # Save to temp file (Whisper needs a file path)
        suffix = os.path.splitext(filename)[1] or ".webm"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        try:
            result = self._whisper_model.transcribe(
                temp_path,
                language="en",
                word_timestamps=True,
                verbose=False,
            )

            transcript = result.get("text", "").strip()
            segments = result.get("segments", [])

            return {
                "transcript": transcript,
                "segments": segments,
                "language": result.get("language", "en"),
            }
        finally:
            os.unlink(temp_path)

    # ─── Speech Analytics ─────────────────────────────────────────────

    async def analyze(self, audio_bytes: bytes, filename: str = "audio.webm") -> dict:
        """
        Full speech analysis pipeline:
        1. Transcribe with Whisper
        2. Calculate speech metrics
        3. Extract audio features with librosa
        """
        # Step 1: Transcribe
        transcription = await self.transcribe(audio_bytes, filename)
        transcript = transcription["transcript"]
        segments = transcription["segments"]

        # Step 2: Calculate text-based metrics
        text_metrics = self._analyze_text(transcript, segments)

        # Step 3: Extract audio features
        audio_metrics = self._analyze_audio(audio_bytes, filename)

        # Step 4: Compute confidence score
        confidence = self._compute_confidence(text_metrics, audio_metrics)

        return {
            "transcript": transcript,
            "words_per_minute": text_metrics["wpm"],
            "pause_count": text_metrics["pause_count"],
            "average_pause_duration": text_metrics["avg_pause_duration"],
            "filler_word_count": text_metrics["filler_count"],
            "filler_words_detected": text_metrics["fillers_found"],
            "filler_rate": text_metrics["filler_rate"],
            "word_count": text_metrics["word_count"],
            "confidence_score": round(confidence, 3),
            "total_duration_seconds": audio_metrics.get("duration", 0),
            "speaking_rate_variability": audio_metrics.get("rate_variability", 0),
            "pitch_mean": audio_metrics.get("pitch_mean", 0),
            "pitch_std": audio_metrics.get("pitch_std", 0),
            "energy_mean": audio_metrics.get("energy_mean", 0),
            "energy_std": audio_metrics.get("energy_std", 0),
        }

    def _analyze_text(self, transcript: str, segments: list) -> dict:
        """Analyze the transcript text for speech quality metrics."""
        words = transcript.split()
        word_count = len(words)
        lower_transcript = transcript.lower()

        # ── Filler words ──────────────────────────────────────────
        fillers_found = []
        filler_count = 0
        for filler in FILLER_WORDS:
            count = lower_transcript.count(filler)
            if count > 0:
                filler_count += count
                fillers_found.extend([filler] * count)

        filler_rate = filler_count / max(word_count, 1)

        # ── Pauses (from segment timing) ──────────────────────────
        pause_count = 0
        pause_durations = []

        for i in range(1, len(segments)):
            prev_end = segments[i - 1].get("end", 0)
            curr_start = segments[i].get("start", 0)
            gap = curr_start - prev_end
            if gap > 0.5:  # Pause threshold: 500ms
                pause_count += 1
                pause_durations.append(gap)

        avg_pause_duration = (
            sum(pause_durations) / len(pause_durations)
            if pause_durations
            else 0
        )

        # ── WPM ──────────────────────────────────────────────────
        if segments:
            total_speech_time = segments[-1].get("end", 0) - segments[0].get("start", 0)
        else:
            total_speech_time = 0

        wpm = (word_count / max(total_speech_time, 1)) * 60 if total_speech_time > 0 else 0

        return {
            "word_count": word_count,
            "wpm": round(wpm, 1),
            "pause_count": pause_count,
            "avg_pause_duration": round(avg_pause_duration, 2),
            "filler_count": filler_count,
            "fillers_found": fillers_found,
            "filler_rate": round(filler_rate, 4),
        }

    def _analyze_audio(self, audio_bytes: bytes, filename: str) -> dict:
        """Extract audio features using librosa."""
        try:
            import librosa
            import soundfile as sf
        except ImportError:
            logger.warning("librosa/soundfile not available, skipping audio analysis")
            return {"duration": 0}

        suffix = os.path.splitext(filename)[1] or ".webm"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        try:
            y, sr = librosa.load(temp_path, sr=16000)
            duration = librosa.get_duration(y=y, sr=sr)

            # Pitch (F0) analysis
            pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)

            pitch_arr = np.array(pitch_values) if pitch_values else np.array([0])

            # Energy (RMS)
            rms = librosa.feature.rms(y=y)[0]

            # Speaking rate variability (via onset detection)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            rate_variability = float(np.std(onset_env)) if len(onset_env) > 1 else 0

            return {
                "duration": round(duration, 2),
                "pitch_mean": round(float(np.mean(pitch_arr)), 2),
                "pitch_std": round(float(np.std(pitch_arr)), 2),
                "energy_mean": round(float(np.mean(rms)), 6),
                "energy_std": round(float(np.std(rms)), 6),
                "rate_variability": round(rate_variability, 4),
            }
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {"duration": 0}
        finally:
            os.unlink(temp_path)

    def _compute_confidence(self, text_metrics: dict, audio_metrics: dict) -> float:
        """
        Compute a 0-1 confidence score based on speech characteristics.
        Higher score = more confident speaker.
        """
        score = 0.5  # baseline

        # WPM: ideal range 120-160
        wpm = text_metrics["wpm"]
        if 120 <= wpm <= 160:
            score += 0.15
        elif 100 <= wpm <= 180:
            score += 0.08
        elif wpm < 80 or wpm > 200:
            score -= 0.1

        # Fewer fillers = more confident
        filler_rate = text_metrics["filler_rate"]
        if filler_rate < 0.02:
            score += 0.15
        elif filler_rate < 0.05:
            score += 0.08
        elif filler_rate > 0.10:
            score -= 0.15

        # Fewer long pauses = more confident
        pause_count = text_metrics["pause_count"]
        word_count = text_metrics["word_count"]
        if word_count > 0:
            pause_rate = pause_count / word_count
            if pause_rate < 0.02:
                score += 0.1
            elif pause_rate > 0.08:
                score -= 0.1

        # Energy stability (lower std relative to mean = steadier voice)
        energy_mean = audio_metrics.get("energy_mean", 0)
        energy_std = audio_metrics.get("energy_std", 0)
        if energy_mean > 0:
            energy_cv = energy_std / energy_mean
            if energy_cv < 0.5:
                score += 0.1  # steady voice
            elif energy_cv > 1.5:
                score -= 0.1  # very unstable

        return max(0.0, min(1.0, score))


# Singleton
speech_processor = SpeechProcessor()
