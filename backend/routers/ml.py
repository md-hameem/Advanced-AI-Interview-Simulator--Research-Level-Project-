"""
Advanced AI Interview Simulator - ML Model API Router
Endpoints for ML model predictions and model status.
"""
import logging
from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ml", tags=["ml"])


class TextInput(BaseModel):
    text: str


class QAInput(BaseModel):
    question: str
    answer: str


class CodeInput(BaseModel):
    code: str


@router.get("/status")
def ml_model_status():
    """Check which ML models are loaded and available."""
    try:
        from ml.inference import get_ml_service
        service = get_ml_service()
        return {
            "loaded": True,
            "models": service.get_available_models(),
        }
    except Exception as e:
        return {
            "loaded": False,
            "error": str(e),
            "models": {},
        }


@router.post("/predict/answer-quality")
def predict_answer_quality(body: QAInput):
    """Predict answer quality score using the trained DeBERTa model."""
    from ml.inference import get_ml_service
    service = get_ml_service()
    score = service.predict_answer_quality(body.question, body.answer)
    return {"score": score, "model": "answer_quality"}


@router.post("/predict/communication")
def predict_communication(body: TextInput):
    """Predict communication clarity/fluency/structure scores."""
    from ml.inference import get_ml_service
    service = get_ml_service()
    scores = service.predict_communication(body.text)
    return {"scores": scores, "model": "communication"}


@router.post("/predict/star")
def predict_star(body: TextInput):
    """Predict STAR component scores from behavioral answer."""
    from ml.inference import get_ml_service
    service = get_ml_service()
    scores = service.predict_star(body.text)
    return {"scores": scores, "model": "star_analyzer"}


@router.post("/predict/code-quality")
def predict_code_quality(body: CodeInput):
    """Predict code quality/efficiency/style scores."""
    from ml.inference import get_ml_service
    service = get_ml_service()
    scores = service.predict_code_quality(body.code)
    return {"scores": scores, "model": "code_evaluator"}
