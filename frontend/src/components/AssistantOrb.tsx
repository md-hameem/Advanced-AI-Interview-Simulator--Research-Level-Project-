"use client";

import { useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, MeshDistortMaterial } from "@react-three/drei";
import * as THREE from "three";

interface OrbProps {
  isSpeaking: boolean;
  isAnalyzing: boolean;
}

function Orb({ isSpeaking, isAnalyzing }: OrbProps) {
  const sphereRef = useRef<THREE.Mesh>(null);
  
  // Transition targets for smooth interpolation
  const [targetDistort] = useState(() => new THREE.Vector2(0.4, 0.4));
  const [targetSpeed] = useState(() => new THREE.Vector2(2, 2));
  
  // Update targets based on state
  if (isSpeaking) {
    targetDistort.set(0.6, 0.6);
    targetSpeed.set(5, 5);
  } else if (isAnalyzing) {
    targetDistort.set(0.8, 0.8);
    targetSpeed.set(1.5, 1.5);
  } else {
    // Idle state
    targetDistort.set(0.3, 0.3);
    targetSpeed.set(1.5, 1.5);
  }

  useFrame((state, delta) => {
    if (sphereRef.current) {
      sphereRef.current.rotation.y += delta * 0.5;
      sphereRef.current.rotation.x += delta * 0.2;
    }
  });

  // Choose color based on state
  const emissiveColor = isAnalyzing 
    ? "#a855f7" // Purple when analyzing
    : isSpeaking 
      ? "#3b82f6" // Blue when speaking
      : "#10b981"; // Green when idle listening

  return (
    <Sphere ref={sphereRef} args={[1, 100, 100]} scale={1.5}>
      <MeshDistortMaterial
        color="#000000"
        emissive={emissiveColor}
        emissiveIntensity={1.5}
        distort={isSpeaking ? 0.6 : isAnalyzing ? 0.8 : 0.3}
        speed={isSpeaking ? 5 : isAnalyzing ? 1.5 : 2}
        roughness={0.2}
        metalness={0.8}
        wireframe={isAnalyzing}
      />
    </Sphere>
  );
}

export default function AssistantOrb(props: OrbProps) {
  return (
    <div className="w-48 h-48 sm:w-64 sm:h-64 mx-auto relative glow">
      <Canvas camera={{ position: [0, 0, 4] }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#fff" />
        <Orb {...props} />
      </Canvas>
    </div>
  );
}
