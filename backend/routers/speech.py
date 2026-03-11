"""
Advanced AI Interview Simulator - Speech API Router
Endpoints for audio transcription, speech analysis, and speech-based answer submission.
"""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session

from database import get_db
from models.interview import Interview, InterviewQuestion, InterviewStatus
from services.speech_processor import speech_processor
from services.interview_agent import interview_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/speech", tags=["speech"])


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe an audio file to text using Whisper ASR."""
    if not audio.content_type or not (
        audio.content_type.startswith("audio/") or audio.content_type == "application/octet-stream"
    ):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    audio_bytes = await audio.read()
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file too small")

    try:
        result = await speech_processor.transcribe(audio_bytes, audio.filename or "audio.webm")
        return {
            "transcript": result["transcript"],
            "language": result["language"],
        }
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/analyze")
async def analyze_speech(audio: UploadFile = File(...)):
    """
    Full speech analysis: transcription + metrics.
    Returns transcript, WPM, pauses, fillers, confidence score, and audio features.
    """
    audio_bytes = await audio.read()
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file too small")

    try:
        metrics = await speech_processor.analyze(audio_bytes, audio.filename or "audio.webm")
        return metrics
    except Exception as e:
        logger.error(f"Speech analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Speech analysis failed: {str(e)}")


@router.post("/answer/{interview_id}/{question_id}")
async def submit_speech_answer(
    interview_id: str,
    question_id: str,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Submit an answer via speech: transcribe, analyze speech, evaluate answer.
    Combines speech metrics with text evaluation.
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if interview.status != InterviewStatus.IN_PROGRESS.value:
        raise HTTPException(status_code=400, detail="Interview is not in progress")

    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id,
        InterviewQuestion.interview_id == interview_id,
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.answer_text:
        raise HTTPException(status_code=400, detail="Question already answered")

    audio_bytes = await audio.read()

    try:
        # Step 1: Full speech analysis
        speech_metrics = await speech_processor.analyze(audio_bytes, audio.filename or "audio.webm")
        transcript = speech_metrics["transcript"]

        if not transcript.strip():
            raise HTTPException(status_code=400, detail="Could not transcribe any speech from the audio")

        # Step 2: Store speech metrics on the question
        question.speech_metrics = {
            "wpm": speech_metrics["words_per_minute"],
            "pause_count": speech_metrics["pause_count"],
            "filler_count": speech_metrics["filler_word_count"],
            "filler_words": speech_metrics["filler_words_detected"],
            "filler_rate": speech_metrics["filler_rate"],
            "confidence_score": speech_metrics["confidence_score"],
            "duration": speech_metrics["total_duration_seconds"],
            "pitch_mean": speech_metrics["pitch_mean"],
            "pitch_std": speech_metrics["pitch_std"],
            "energy_mean": speech_metrics["energy_mean"],
        }
        db.commit()

        # Step 3: Evaluate the transcribed text using the interview agent
        result = await interview_agent.submit_answer(db, interview_id, question_id, transcript)

        # Step 4: Combine speech metrics into the response
        result["speech_metrics"] = speech_metrics

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech answer submission failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process speech answer: {str(e)}")
