from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.interview import Interview
from services.emotion_detector import emotion_detector

router = APIRouter(prefix="/api/vision", tags=["vision"])

class FrameUpload(BaseModel):
    image_base64: str

@router.post("/analyze-frame/{interview_id}")
async def analyze_frame(interview_id: str, data: FrameUpload, db: Session = Depends(get_db)):
    """Analyze a single video frame from the webcam for emotion context."""
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    # Analyze frame synchronously (fast enough with mock/fer, might need async for deepface)
    result = emotion_detector.analyze_frame(data.image_base64)
    
    # Store aggregated history in interview context
    context = interview.context or {}
    emotion_history = context.get("emotion_history", [])
    emotion_history.append(result)
    
    # Keep up to 200 frames to avoid bloating the JSON context
    if len(emotion_history) > 200:
        emotion_history = emotion_history[-200:]
        
    context["emotion_history"] = emotion_history
    interview.context = context
    
    db.flag_modified(interview, "context")
    db.commit()
    
    return {"status": "ok", "dominant_emotion": result.get("dominant_emotion")}
