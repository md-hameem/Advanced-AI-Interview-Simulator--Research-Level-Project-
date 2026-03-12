"""
ML Pipeline - Production Inference Service
Loads trained models and provides a unified prediction API.
"""
import os
import logging
import torch
import numpy as np

from ml.config import TrainingConfig

logger = logging.getLogger(__name__)


class MLInferenceService:
    """
    Unified inference service that loads all trained models
    and provides prediction methods for the backend API.
    """

    def __init__(self):
        self.config = TrainingConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._answer_quality = None
        self._communication = None
        self._star_analyzer = None
        self._code_evaluator = None
        self._meta_scorer = None
        self._loaded = False

    def load_all(self):
        """Load all available trained models."""
        logger.info("Loading ML models...")

        try:
            self._load_answer_quality()
        except Exception as e:
            logger.warning(f"Answer quality model not available: {e}")

        try:
            self._load_communication()
        except Exception as e:
            logger.warning(f"Communication model not available: {e}")

        try:
            self._load_star_analyzer()
        except Exception as e:
            logger.warning(f"STAR analyzer model not available: {e}")

        try:
            self._load_code_evaluator()
        except Exception as e:
            logger.warning(f"Code evaluator model not available: {e}")

        try:
            self._load_meta_scorer()
        except Exception as e:
            logger.warning(f"Meta scorer model not available: {e}")

        self._loaded = True
        logger.info("ML models loaded.")

    def _load_answer_quality(self):
        from ml.models.answer_quality import AnswerQualityTrainer
        trainer = AnswerQualityTrainer(self.config.answer_quality)
        trainer.load(self.config.answer_quality.output_dir)
        self._answer_quality = trainer

    def _load_communication(self):
        from ml.models.communication import CommunicationTrainer
        trainer = CommunicationTrainer(self.config.communication)
        trainer.load(self.config.communication.output_dir)
        self._communication = trainer

    def _load_star_analyzer(self):
        from ml.models.star_analyzer import StarAnalyzerTrainer
        trainer = StarAnalyzerTrainer(self.config.star_analyzer)
        trainer.load(self.config.star_analyzer.output_dir)
        self._star_analyzer = trainer

    def _load_code_evaluator(self):
        from ml.models.code_evaluator import CodeEvaluatorTrainer
        trainer = CodeEvaluatorTrainer(self.config.code_evaluator)
        trainer.load(self.config.code_evaluator.output_dir)
        self._code_evaluator = trainer

    def _load_meta_scorer(self):
        from ml.models.meta_scorer import MetaScorer
        scorer = MetaScorer(self.config.meta_scorer)
        scorer.load(self.config.meta_scorer.output_dir)
        self._meta_scorer = scorer

    # ─── Prediction Methods ──────────────────────────────────────────

    @torch.no_grad()
    def predict_answer_quality(self, question: str, answer: str) -> float:
        """Predict answer quality score (0-10)."""
        if not self._answer_quality:
            return -1.0

        text = f"{question} [SEP] {answer}"
        tokens = self._answer_quality.tokenizer(
            text, max_length=512, padding="max_length",
            truncation=True, return_tensors="pt",
        )
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        score = self._answer_quality.model(**tokens)
        return round(float(score.item()), 2)

    @torch.no_grad()
    def predict_communication(self, text: str) -> dict:
        """Predict communication scores (clarity, fluency, structure) each 0-5."""
        if not self._communication:
            return {"clarity": -1, "fluency": -1, "structure": -1}

        tokens = self._communication.tokenizer(
            text, max_length=384, padding="max_length",
            truncation=True, return_tensors="pt",
        )
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        scores = self._communication.model(**tokens)
        s = scores.squeeze(0).cpu().numpy()
        return {
            "clarity": round(float(s[0]), 2),
            "fluency": round(float(s[1]), 2),
            "structure": round(float(s[2]), 2),
        }

    @torch.no_grad()
    def predict_star(self, text: str) -> dict:
        """Predict STAR component scores (situation, task, action, result) each 0-5."""
        if not self._star_analyzer:
            return {"situation": -1, "task": -1, "action": -1, "result": -1}

        tokens = self._star_analyzer.tokenizer(
            text, max_length=512, padding="max_length",
            truncation=True, return_tensors="pt",
        )
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        scores = self._star_analyzer.model(**tokens)
        s = scores.squeeze(0).cpu().numpy()
        return {
            "situation": round(float(s[0]), 2),
            "task": round(float(s[1]), 2),
            "action": round(float(s[2]), 2),
            "result": round(float(s[3]), 2),
        }

    @torch.no_grad()
    def predict_code_quality(self, code: str) -> dict:
        """Predict code quality scores (quality, efficiency, style) each 0-5."""
        if not self._code_evaluator:
            return {"quality": -1, "efficiency": -1, "style": -1}

        tokens = self._code_evaluator.tokenizer(
            code, max_length=512, padding="max_length",
            truncation=True, return_tensors="pt",
        )
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        scores = self._code_evaluator.model(**tokens)
        s = scores.squeeze(0).cpu().numpy()
        return {
            "quality": round(float(s[0]), 2),
            "efficiency": round(float(s[1]), 2),
            "style": round(float(s[2]), 2),
        }

    def predict_final_score(self, features: dict) -> float:
        """Predict final aggregated score (0-10) from all model outputs."""
        if not self._meta_scorer:
            return -1.0
        return self._meta_scorer.predict(features)

    def get_available_models(self) -> dict:
        """Return which models are loaded and available."""
        return {
            "answer_quality": self._answer_quality is not None,
            "communication": self._communication is not None,
            "star_analyzer": self._star_analyzer is not None,
            "code_evaluator": self._code_evaluator is not None,
            "meta_scorer": self._meta_scorer is not None,
        }


# Lazy-initialized singleton
_service = None


def get_ml_service() -> MLInferenceService:
    """Get or create the ML inference service singleton."""
    global _service
    if _service is None:
        _service = MLInferenceService()
        # Attempt to load models (non-fatal if not trained yet)
        try:
            _service.load_all()
        except Exception as e:
            logger.warning(f"ML models not loaded (not trained yet?): {e}")
    return _service
