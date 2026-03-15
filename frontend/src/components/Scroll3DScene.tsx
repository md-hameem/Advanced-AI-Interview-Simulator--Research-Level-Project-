"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Points, PointMaterial, Environment, Sphere } from "@react-three/drei";
import * as THREE from "three";
import { useScroll, useTransform } from "framer-motion";

// Generates a floating field of "AI neural stars"
function ParticleSwarm({ scrollYProgress }: { scrollYProgress: any }) {
  const ref = useRef<THREE.Points>(null);
  
  // Create 5000 random points within a sphere
  const sphere = useMemo(() => {
    const positions = new Float32Array(5000 * 3);
    for (let i = 0; i < 5000; i++) {
      const radius = 2.5; // Wider radius for better scroll immersion
      const theta = 2 * Math.PI * Math.random();
      const phi = Math.acos(2 * Math.random() - 1);
      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);
      
      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;
    }
    return positions;
  }, []);

  useFrame((state, delta) => {
    if (ref.current) {
      // Natural slow rotation
      ref.current.rotation.x -= delta / 30;
      ref.current.rotation.y -= delta / 40;
      
      // Scroll-driven explosion & rotation
      const progress = scrollYProgress.get();
      // Scale from 1 up to 2.5 as we scroll
      const scale = Math.max(0.001, 1 + progress * 1.5);
      ref.current.scale.set(scale, scale, scale);
      
      // Add extra rotation based on scroll position
      ref.current.rotation.z = progress * Math.PI;
    }
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={sphere} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color="#00ffff"
          size={0.004}
          sizeAttenuation={true}
          depthWrite={false}
          opacity={0.8}
        />
      </Points>
    </group>
  );
}

// Glowing inner orb
function CoreOrb({ scrollYProgress }: { scrollYProgress: any }) {
  const orbRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);
  const { camera } = useThree();

  useFrame(({ clock }) => {
    const progress = scrollYProgress.get();

    if (orbRef.current) {
      // Fast spin linked to time + scroll progress
      orbRef.current.rotation.y = clock.getElapsedTime() * 0.2 + progress * Math.PI * 2;
      
      // Scale down the core as we scroll to section 2, disappear by section 3
      const scale = Math.max(0.001, 1 - progress * 1.5);
      orbRef.current.scale.set(scale, scale, scale);
    }
    
    if (materialRef.current) {
      // Pulse emissive intensity
      materialRef.current.emissiveIntensity = Math.max(0, (1 - progress) * (1 + Math.sin(clock.getElapsedTime() * 2) * 0.5));
    }
    
    // Smoothly transition camera position
    // Start at Z=4, push into the sphere as scroll increases
    camera.position.z = THREE.MathUtils.lerp(camera.position.z, 4 - progress * 2.5, 0.1);
  });

  return (
    <Sphere ref={orbRef} args={[0.8, 64, 64]}>
      <meshStandardMaterial
        ref={materialRef}
        color="#000000"
        emissive="#3b82f6"
        emissiveIntensity={1.5}
        roughness={0.1}
        metalness={0.9}
        wireframe={true}
      />
    </Sphere>
  );
}

export default function Scroll3DScene() {
  const { scrollYProgress } = useScroll();

  return (
    <div className="fixed inset-0 -z-10 h-full w-full pointer-events-none bg-black">
      <Canvas camera={{ position: [0, 0, 4] }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#00ffff" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#8b5cf6" />
        <ParticleSwarm scrollYProgress={scrollYProgress} />
        <CoreOrb scrollYProgress={scrollYProgress} />
        <Environment preset="city" />
        
        {/* Soft fog to blend edges into deep black */}
        <fog attach="fog" args={["#000000", 3, 10]} />
      </Canvas>
      
      {/* Heavy vignette to ensure text legibility */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#000000_100%)] opacity-80" />
    </div>
  );
}
