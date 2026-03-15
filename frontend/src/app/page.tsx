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
} from "lucide-react";
import dynamic from "next/dynamic";

const Hero3D = dynamic(() => import("@/components/Hero3D"), { ssr: false });

const features = [
  {
    icon: Brain,
    title: "Adaptive Questioning",
    desc: "AI adjusts difficulty based on your performance in real-time.",
    color: "from-violet-500 to-purple-600",
  },
  {
    icon: Mic,
    title: "Speech Intelligence",
    desc: "Analyze speaking speed, confidence, and communication clarity.",
    color: "from-cyan-500 to-blue-600",
  },
  {
    icon: Code,
    title: "Live Coding Evaluation",
    desc: "Code editor with automated test execution and complexity analysis.",
    color: "from-emerald-500 to-green-600",
  },
  {
    icon: BarChart3,
    title: "Rubric-Based Scoring",
    desc: "Structured evaluation across correctness, depth, clarity, reasoning.",
    color: "from-amber-500 to-orange-600",
  },
  {
    icon: Target,
    title: "STAR Framework Detection",
    desc: "Behavioral answer analysis using Situation-Task-Action-Result.",
    color: "from-rose-500 to-pink-600",
  },
  {
    icon: Sparkles,
    title: "AI-Generated Reports",
    desc: "Professional candidate assessment reports with hiring recommendations.",
    color: "from-indigo-500 to-violet-600",
  },
];

const stats = [
  { value: "5+", label: "ML Models" },
  { value: "6", label: "Evaluation Criteria" },
  { value: "100+", label: "Question Bank" },
  { value: "Real-time", label: "Feedback" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* ── Navbar ──────────────────────────────────────────────────── */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
              <Brain size={20} className="text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight">
              Interview<span className="gradient-text">AI</span>
            </span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="text-sm text-white/60 hover:text-white transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/interview/new"
              className="px-4 py-2 text-sm font-medium rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white hover:opacity-90 transition-opacity"
            >
              Start Interview
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────────────────────────── */}
      <section className="relative pt-32 pb-40 px-6 min-h-[90vh] flex flex-col justify-center overflow-hidden">
        {/* 3D Background */}
        <Hero3D />
        
        {/* Subtle glow overlays to complement the 3D scene */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full bg-brand-500/10 blur-[150px] pointer-events-none" />

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-light text-sm text-brand-300 mb-8 animate-fade-in-up">
            <Sparkles size={14} />
            Research-Level AI System
          </div>

          <h1
            className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6 animate-fade-in-up"
            style={{ animationDelay: "0.1s" }}
          >
            Master Your
            <br />
            <span className="gradient-text glow-text">Technical Interviews</span>
          </h1>

          <p
            className="text-lg md:text-xl text-white/50 max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up"
            style={{ animationDelay: "0.2s" }}
          >
            AI-powered interview simulator with adaptive questioning, multi-model
            evaluation, speech analysis, and professional candidate assessment
            reports.
          </p>

          <div
            className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up"
            style={{ animationDelay: "0.3s" }}
          >
            <Link
              href="/interview/new"
              className="group flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold text-lg hover:shadow-lg hover:shadow-brand-500/25 transition-all duration-300"
            >
              Start Mock Interview
              <ArrowRight
                size={20}
                className="group-hover:translate-x-1 transition-transform"
              />
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-8 py-3.5 rounded-2xl glass-light text-white/80 font-medium text-lg hover:text-white transition-colors"
            >
              <BarChart3 size={20} />
              View Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats ───────────────────────────────────────────────────── */}
      <section className="py-12 px-6">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((s) => (
            <div
              key={s.label}
              className="glass rounded-2xl p-6 text-center hover:scale-[1.02] transition-transform"
            >
              <div className="text-3xl font-bold gradient-text mb-1">{s.value}</div>
              <div className="text-sm text-white/40">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ────────────────────────────────────────────────── */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Multi-Signal{" "}
              <span className="gradient-text">Evaluation Engine</span>
            </h2>
            <p className="text-white/40 max-w-xl mx-auto">
              Not just one model — a full pipeline of specialized AI systems
              that evaluate every aspect of your interview performance.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <div
                key={f.title}
                className="glass rounded-2xl p-6 hover:scale-[1.02] transition-all duration-300 group animate-fade-in-up"
                style={{ animationDelay: `${i * 0.08}s` }}
              >
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                >
                  <f.icon size={22} className="text-white" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-white/40 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it Works ────────────────────────────────────────────── */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-14">
            How It <span className="gradient-text">Works</span>
          </h2>

          <div className="space-y-6">
            {[
              {
                step: "01",
                title: "Set Up Your Profile",
                desc: "Enter your name, target role, experience, and skills for personalized questions.",
                icon: Users,
              },
              {
                step: "02",
                title: "Start the Interview",
                desc: "Choose interview type (technical, behavioral, coding, or mixed) and difficulty level.",
                icon: Zap,
              },
              {
                step: "03",
                title: "Answer Adaptive Questions",
                desc: "AI generates dynamic questions, adjusting difficulty based on your performance.",
                icon: Brain,
              },
              {
                step: "04",
                title: "Get Your Assessment",
                desc: "Receive a comprehensive evaluation report with scores, strengths, and improvement areas.",
                icon: CheckCircle2,
              },
            ].map((item, i) => (
              <div
                key={item.step}
                className="glass rounded-2xl p-6 flex items-start gap-6 hover:scale-[1.01] transition-transform animate-fade-in-up"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <span className="text-4xl font-extrabold gradient-text shrink-0">
                  {item.step}
                </span>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{item.title}</h3>
                  <p className="text-sm text-white/40">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────────── */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center glass rounded-3xl p-12 glow">
          <h2 className="text-3xl font-bold mb-4">Ready to Ace Your Interview?</h2>
          <p className="text-white/40 mb-8">
            Start a mock interview now and get instant AI-powered feedback on
            your technical and communication skills.
          </p>
          <Link
            href="/interview/new"
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold text-lg hover:shadow-lg hover:shadow-brand-500/25 transition-all"
          >
            Begin Interview
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <footer className="py-8 px-6 text-center text-white/20 text-sm border-t border-white/5">
        AI Interview Simulator — Research-Level Project &middot; Built with
        Next.js, FastAPI, and Google Gemini
      </footer>
    </div>
  );
}
