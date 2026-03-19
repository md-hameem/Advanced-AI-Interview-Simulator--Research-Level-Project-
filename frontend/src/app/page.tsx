"use client";

import Link from "next/link";
import {
  Brain,
  Mic,
  Code,
  BarChart3,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Users,
  Target,
  Zap,
  ChevronDown,
} from "lucide-react";
import { motion, useScroll, useTransform, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import MeshGradient from "@/components/MeshGradient";
import BentoCard from "@/components/BentoCard";
import KineticText from "@/components/KineticText";

/* ─── Data ───────────────────────────────────────────────────────────── */

const features = [
  {
    icon: Brain,
    title: "Adaptive Questioning",
    desc: "AI adjusts difficulty in real-time based on your performance, creating a naturally flowing interview.",
    color: "from-violet-500 to-purple-600",
    span: "wide" as const,
  },
  {
    icon: Mic,
    title: "Speech Intelligence",
    desc: "Analyze speaking speed, confidence, and communication clarity.",
    color: "from-cyan-500 to-blue-600",
    span: "default" as const,
  },
  {
    icon: Code,
    title: "Live Coding",
    desc: "Monaco editor with sandbox execution and complexity analysis.",
    color: "from-emerald-500 to-green-600",
    span: "default" as const,
  },
  {
    icon: BarChart3,
    title: "Rubric Scoring",
    desc: "Structured evaluation across correctness, depth, clarity, and reasoning.",
    color: "from-amber-500 to-orange-600",
    span: "default" as const,
  },
  {
    icon: Target,
    title: "STAR Detection",
    desc: "Behavioral answer analysis using Situation-Task-Action-Result framework.",
    color: "from-rose-500 to-pink-600",
    span: "default" as const,
  },
  {
    icon: Sparkles,
    title: "AI Reports",
    desc: "Professional candidate assessment with hiring recommendations and personalized study plans.",
    color: "from-indigo-500 to-violet-600",
    span: "wide" as const,
  },
];

const stats = [
  { value: 5, suffix: "+", label: "ML Models", color: "text-violet-400" },
  { value: 6, suffix: "", label: "Eval Criteria", color: "text-cyan-400" },
  { value: 100, suffix: "+", label: "Questions", color: "text-emerald-400" },
  { value: 4, suffix: "", label: "AI Agents", color: "text-amber-400" },
];

const steps = [
  {
    step: "01",
    title: "Set Up Profile",
    desc: "Enter your name, target role, experience, and skills for personalized questions.",
    icon: Users,
    gradient: "from-violet-500/20 to-purple-600/20",
  },
  {
    step: "02",
    title: "Start Interview",
    desc: "Choose type, difficulty, and AI personality. Meet your interviewer.",
    icon: Zap,
    gradient: "from-cyan-500/20 to-blue-600/20",
  },
  {
    step: "03",
    title: "Answer Questions",
    desc: "AI adapts in real-time. Use voice, text, or code to respond.",
    icon: Brain,
    gradient: "from-emerald-500/20 to-green-600/20",
  },
  {
    step: "04",
    title: "Get Assessment",
    desc: "Comprehensive report with scores, strengths, and a personalized study plan.",
    icon: CheckCircle2,
    gradient: "from-amber-500/20 to-orange-600/20",
  },
];

/* ─── Counter Component ──────────────────────────────────────────────── */

function AnimatedCounter({ value, suffix, color }: { value: number; suffix: string; color: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (!isInView) return;
    let start = 0;
    const duration = 2000;
    const increment = value / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [isInView, value]);

  return (
    <span ref={ref} className={`text-5xl md:text-6xl font-bold tabular-nums ${color}`}>
      {count}{suffix}
    </span>
  );
}

/* ─── Page ───────────────────────────────────────────────────────────── */

export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const horizontalRef = useRef<HTMLDivElement>(null);
  const navRef = useRef<HTMLElement>(null);

  // Hero parallax
  const { scrollYProgress: heroScroll } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
  });
  const heroY = useTransform(heroScroll, [0, 1], [0, -200]);
  const heroOpacity = useTransform(heroScroll, [0, 0.6], [1, 0]);
  const heroScale = useTransform(heroScroll, [0, 0.6], [1, 0.85]);

  // Horizontal scroll for "How it Works"
  const { scrollYProgress: horizontalScroll } = useScroll({
    target: horizontalRef,
    offset: ["start end", "end start"],
  });
  const horizontalX = useTransform(horizontalScroll, [0, 1], ["0%", "-40%"]);

  // Navbar visibility (appears after hero)
  const navOpacity = useTransform(heroScroll, [0.3, 0.5], [0, 1]);

  return (
    <div className="relative">
      {/* ── Mesh Gradient Background ─────────────────────────────────── */}
      <MeshGradient />

      {/* ── Floating Navbar (fades in after hero scroll) ─────────────── */}
      <motion.nav
        ref={navRef}
        style={{ opacity: navOpacity }}
        className="fixed top-4 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-2xl glass-light flex items-center gap-6"
      >
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
            <Brain size={16} className="text-white" />
          </div>
          <span className="text-sm font-bold tracking-tight">
            Interview<span className="gradient-text">AI</span>
          </span>
        </Link>
        <Link
          href="/dashboard"
          className="text-xs text-white/50 hover:text-white transition-colors"
        >
          Dashboard
        </Link>
        <Link
          href="/interview/new"
          className="px-4 py-1.5 text-xs font-medium rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white hover:opacity-90 transition-opacity"
        >
          Start Interview
        </Link>
      </motion.nav>

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* ── SECTION 1: Hero ──────────────────────────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════ */}
      <section ref={heroRef} className="relative min-h-[100vh] flex flex-col items-center justify-center px-6 overflow-hidden">
        <motion.div
          style={{ y: heroY, opacity: heroOpacity, scale: heroScale }}
          className="text-center relative z-10 max-w-5xl mx-auto"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="inline-flex items-center gap-2 px-5 py-2 rounded-full glass-light text-sm text-white/60 mb-10"
          >
            <Sparkles size={14} className="text-brand-400" />
            Research-Level AI System
          </motion.div>

          {/* Kinetic Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="text-[clamp(3rem,10vw,8rem)] font-extrabold leading-[0.95] tracking-[-0.03em] mb-8"
          >
            Master Your
            <br />
            <span className="gradient-text glow-text">Technical</span>
            <br />
            <span className="gradient-text-cyan">Interviews</span>
          </motion.h1>

          {/* Subtext */}
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            className="text-lg md:text-xl text-white/35 max-w-xl mx-auto mb-12 leading-relaxed font-light"
          >
            AI-powered simulator with adaptive questioning, multi-model evaluation,
            and professional candidate assessment.
          </motion.p>

          {/* CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.9 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              href="/interview/new"
              className="group flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold text-lg hover:shadow-lg hover:shadow-brand-500/20 transition-all duration-500 hover:scale-[1.03]"
            >
              Start Mock Interview
              <ArrowRight
                size={20}
                className="group-hover:translate-x-1.5 transition-transform duration-300"
              />
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-8 py-4 rounded-2xl glass text-white/60 font-medium text-lg hover:text-white/90 hover:bg-white/[0.04] transition-all duration-300"
            >
              <BarChart3 size={18} />
              Dashboard
            </Link>
          </motion.div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        >
          <span className="text-[10px] uppercase tracking-[0.2em] text-white/20">Scroll</span>
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          >
            <ChevronDown size={16} className="text-white/20" />
          </motion.div>
        </motion.div>
      </section>

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* ── SECTION 2: Stats ─────────────────────────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════ */}
      <section className="relative min-h-[60vh] flex items-center justify-center px-6 py-32">
        <div className="max-w-5xl mx-auto w-full">
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="text-center text-white/30 text-sm uppercase tracking-[0.2em] mb-16"
          >
            By the numbers
          </motion.p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((s, i) => (
              <BentoCard key={s.label} delay={i * 0.1} className="text-center">
                <AnimatedCounter value={s.value} suffix={s.suffix} color={s.color} />
                <p className="text-white/30 text-sm mt-3 font-medium">
                  {s.label}
                </p>
              </BentoCard>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* ── SECTION 3: Features Bento Grid ───────────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════ */}
      <section className="relative px-6 py-32">
        <div className="max-w-6xl mx-auto">
          {/* Section Title */}
          <KineticText
            className="text-center mb-20"
            scrollRange={[0, 0.3]}
            scaleRange={[1, 0.95]}
            opacityRange={[1, 1]}
            yRange={[0, -30]}
          >
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6 }}
              className="text-white/30 text-sm uppercase tracking-[0.2em] mb-6"
            >
              Evaluation Engine
            </motion.p>
            <motion.h2
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="text-4xl md:text-6xl font-bold leading-tight"
            >
              Multi-Signal
              <br />
              <span className="gradient-text">Intelligence</span>
            </motion.h2>
          </KineticText>

          {/* Bento Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 auto-rows-[minmax(180px,auto)]">
            {features.map((f, i) => (
              <BentoCard key={f.title} delay={i * 0.08} span={f.span}>
                <div className="flex flex-col h-full justify-between">
                  <div>
                    <div
                      className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-5 animate-float`}
                      style={{ animationDelay: `${i * 0.3}s` }}
                    >
                      <f.icon size={22} className="text-white" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2 text-white/90">{f.title}</h3>
                    <p className="text-sm text-white/35 leading-relaxed">{f.desc}</p>
                  </div>
                </div>
              </BentoCard>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* ── SECTION 4: How It Works (Horizontal Scroll) ──────────────── */}
      {/* ══════════════════════════════════════════════════════════════ */}
      <section ref={horizontalRef} className="relative py-32 overflow-hidden">
        <div className="max-w-6xl mx-auto px-6 mb-16">
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="text-white/30 text-sm uppercase tracking-[0.2em] mb-6"
          >
            The Process
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-4xl md:text-6xl font-bold"
          >
            How It <span className="gradient-text-cyan">Works</span>
          </motion.h2>
        </div>

        <motion.div style={{ x: horizontalX }} className="px-6">
          <div className="horizontal-scroll-container">
            {steps.map((item, i) => (
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.7, delay: i * 0.15 }}
                key={item.step}
                className={`bento-card w-[340px] md:w-[400px] shrink-0 bg-gradient-to-br ${item.gradient}`}
              >
                <span className="text-6xl font-extrabold gradient-text opacity-40 block mb-4">
                  {item.step}
                </span>
                <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center mb-4">
                  <item.icon size={20} className="text-white/60" />
                </div>
                <h3 className="font-semibold text-xl mb-2 text-white/90">{item.title}</h3>
                <p className="text-sm text-white/35 leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* ── SECTION 5: CTA ───────────────────────────────────────────── */}
      {/* ══════════════════════════════════════════════════════════════ */}
      <section className="relative min-h-[80vh] flex flex-col items-center justify-center px-6 py-32 overflow-hidden">
        {/* Pulsing gradient glow behind CTA */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[600px] h-[600px] rounded-full bg-brand-500/[0.06] blur-[150px] animate-pulse-glow" />
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="text-center relative z-10 max-w-3xl"
        >
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight"
          >
            Ready to
            <br />
            <span className="gradient-text glow-text">Ace It?</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-white/30 mb-10 text-lg"
          >
            Start your mock interview and get instant AI-powered feedback.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <Link
              href="/interview/new"
              className="group inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold text-xl hover:shadow-2xl hover:shadow-brand-500/30 transition-all duration-500 hover:scale-[1.04]"
            >
              Begin Interview
              <ArrowRight
                size={22}
                className="group-hover:translate-x-2 transition-transform duration-300"
              />
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <footer className="py-12 px-6 text-center text-white/15 text-xs tracking-wide border-t border-white/[0.03]">
        AI Interview Simulator &middot; Research-Level Project &middot; Built with
        Next.js, FastAPI &amp; Groq
      </footer>
    </div>
  );
}
