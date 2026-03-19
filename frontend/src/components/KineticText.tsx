"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

interface KineticTextProps {
  children: React.ReactNode;
  className?: string;
  /** Scroll range [start, end] as fractions. Default: [0, 0.5] */
  scrollRange?: [number, number];
  /** Scale range [start, end]. Default: [1, 0.6] */
  scaleRange?: [number, number];
  /** Opacity range [start, end]. Default: [1, 0] */
  opacityRange?: [number, number];
  /** Y-offset range [start, end] in px. Default: [0, -100] */
  yRange?: [number, number];
}

export default function KineticText({
  children,
  className = "",
  scrollRange = [0, 0.5],
  scaleRange = [1, 0.6],
  opacityRange = [1, 0],
  yRange = [0, -100],
}: KineticTextProps) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const scale = useTransform(scrollYProgress, scrollRange, scaleRange);
  const opacity = useTransform(scrollYProgress, scrollRange, opacityRange);
  const y = useTransform(scrollYProgress, scrollRange, yRange);

  return (
    <motion.div
      ref={ref}
      style={{ scale, opacity, y }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
