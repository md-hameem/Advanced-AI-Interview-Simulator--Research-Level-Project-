"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import api from "@/lib/api";

interface UseWebcamReturn {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  isWebcamActive: boolean;
  startWebcam: () => Promise<void>;
  stopWebcam: () => void;
  error: string | null;
}

/**
 * Hook for browser webcam access and automated frame capture for emotion analysis.
 */
export function useWebcam(interviewId: string): UseWebcamReturn {
  const [isWebcamActive, setIsWebcamActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const captureAndSendFrame = useCallback(async () => {
    if (!videoRef.current || !isWebcamActive) return;

    const video = videoRef.current;
    if (video.videoWidth === 0 || video.videoHeight === 0) return;

    // Create a canvas to extract the frame
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Scale down image to save bandwidth (e.g., 640x480 max)
    const dataUrl = canvas.toDataURL("image/jpeg", 0.7);
    
    // Send to backend
    try {
      await api.post(`/vision/analyze-frame/${interviewId}`, {
        image_base64: dataUrl.split(",")[1], // Remove metadata prefix
      });
    } catch (err) {
      console.warn("Failed to send video frame:", err);
    }
  }, [interviewId, isWebcamActive]);

  const startWebcam = useCallback(async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } },
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      
      setIsWebcamActive(true);

      // Start capturing frames every 4 seconds
      intervalRef.current = setInterval(captureAndSendFrame, 4000);
    } catch (err) {
      if (err instanceof DOMException && err.name === "NotAllowedError") {
        setError("Camera access denied. Please allow camera permissions.");
      } else {
        setError("Failed to start camera. Check your device.");
      }
    }
  }, [captureAndSendFrame]);

  const stopWebcam = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    setIsWebcamActive(false);
  }, []);

  // Ensure cleanup on unmount
  useEffect(() => {
    return () => {
      stopWebcam();
    };
  }, [stopWebcam]);

  return {
    videoRef,
    isWebcamActive,
    startWebcam,
    stopWebcam,
    error,
  };
}
