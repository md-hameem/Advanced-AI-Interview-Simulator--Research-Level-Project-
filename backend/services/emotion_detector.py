"""
Advanced AI Interview Simulator - Emotion Detection Service
Analyzes video frames for candidate stress, confidence, and engagement levels.
"""
import base64
import cv2
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Try importing DeepFace, fallback gracefully if not installed
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    logger.warning("DeepFace not installed. Using fallback mock emotion detection. Run `pip install deepface opencv-python` to enable real analysis.")


class EmotionDetector:
    """Service to analyze facial expressions from video frames."""
    
    def analyze_frame(self, image_base64: str) -> Dict[str, Any]:
        """
        Takes a base64 encoded JPEG frame from the webcam,
        runs emotion detection, and returns the dominant emotion and confidence metrics.
        """
        try:
            # Decode base64 to OpenCV image format
            img_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Failed to decode image.")
                
            if DEEPFACE_AVAILABLE:
                # Run DeepFace emotion analysis
                result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
                # handle list or dict return
                res_dict = result[0] if isinstance(result, list) else result
                
                dominant = res_dict.get('dominant_emotion', 'neutral')
                emotions = res_dict.get('emotion', {})
                
                # Map to intuitive interview metrics
                return {
                    "dominant_emotion": dominant,
                    "stress_level": emotions.get('fear', 0) + emotions.get('sad', 0) + emotions.get('angry', 0),
                    "confidence_level": emotions.get('happy', 0) + emotions.get('neutral', 0) * 0.5,
                    "confusion_level": emotions.get('surprise', 0) + emotions.get('disgust', 0) * 0.5,
                }
            else:
                # Fallback implementation if DeepFace is missing
                # Simulate realistic variation for demo purposes
                return {
                    "dominant_emotion": "neutral",
                    "stress_level": float(np.random.normal(15, 5)),
                    "confidence_level": float(np.random.normal(70, 10)),
                    "confusion_level": float(np.random.normal(10, 5)),
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return {
                "dominant_emotion": "unknown",
                "stress_level": 0.0,
                "confidence_level": 50.0,
                "confusion_level": 0.0,
                "error": str(e)
            }

emotion_detector = EmotionDetector()
