"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Brain,
  ArrowLeft,
  ArrowRight,
  User,
  Briefcase,
  Code,
  MessageSquare,
  Layers,
  Zap,
  Gauge,
  GraduationCap,
} from "lucide-react";
import { createCandidate, createInterview } from "@/lib/api";

const interviewTypes = [
  {
    id: "mixed",
    label: "Mixed",
    desc: "Technical + Behavioral + Coding",
    icon: Layers,
    color: "from-violet-500 to-purple-600",
  },
  {
    id: "technical",
    label: "Technical",
    desc: "Data structures, algorithms, concepts",
    icon: Brain,
    color: "from-cyan-500 to-blue-600",
  },
  {
    id: "coding",
    label: "Coding",
    desc: "Problem solving and code evaluation",
    icon: Code,
    color: "from-emerald-500 to-green-600",
  },
  {
    id: "behavioral",
    label: "Behavioral",
    desc: "Leadership, teamwork, STAR method",
    icon: MessageSquare,
    color: "from-amber-500 to-orange-600",
  },
  {
    id: "system_design",
    label: "System Design",
    desc: "Architecture and scalability",
    icon: Zap,
    color: "from-rose-500 to-pink-600",
  },
];

const difficulties = [
  { id: "easy", label: "Easy", desc: "Junior / Entry-level", color: "text-emerald-400" },
  { id: "medium", label: "Medium", desc: "Mid-level / 2-5 years", color: "text-amber-400" },
  { id: "hard", label: "Hard", desc: "Senior / 5+ years", color: "text-orange-400" },
  { id: "expert", label: "Expert", desc: "Staff / Principal", color: "text-rose-400" },
];

const personas = [
  { id: "default", label: "Default", desc: "Balanced standard technical interview" },
  { id: "google", label: "Google", desc: "Rigorous focus on algorithmic optimality" },
  { id: "amazon", label: "Amazon", desc: "Focus on Leadership Principles & STAR" },
  { id: "startup", label: "Startup", desc: "Focus on impact, speed, and real-world delivery" },
];

export default function NewInterviewPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Form state
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [experience, setExperience] = useState(0);
  const [skills, setSkills] = useState("");
  const [interviewType, setInterviewType] = useState("mixed");
  const [difficulty, setDifficulty] = useState("medium");
  const [persona, setPersona] = useState("default");
  const [numQuestions, setNumQuestions] = useState(5);

  const handleStart = async () => {
    if (!name.trim()) {
      setError("Please enter your name.");
      return;
    }
    setLoading(true);
    setError("");

    try {
      // 1. Create candidate
      const candidate = await createCandidate({
        name: name.trim(),
        email: email.trim() || undefined,
        target_role: targetRole.trim() || undefined,
        experience_years: experience,
        skills: skills
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      });

      // 2. Create interview
      const interview = await createInterview({
        candidate_id: candidate.id,
        interview_type: interviewType,
        difficulty,
        persona,
        total_questions: numQuestions,
      });

      // 3. Navigate to interview session
      router.push(`/interview/${interview.id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to start interview. Is the backend running?";
      setError(msg);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Navbar */}
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
        </div>
      </nav>

      <div className="max-w-2xl mx-auto pt-28 pb-16 px-6">
        <Link
          href="/"
          className="inline-flex items-center gap-1 text-sm text-white/40 hover:text-white/70 transition-colors mb-8"
        >
          <ArrowLeft size={16} />
          Back to Home
        </Link>

        <h1 className="text-3xl font-bold mb-2">
          New <span className="gradient-text">Interview</span>
        </h1>
        <p className="text-white/40 mb-10">Set up your mock interview session.</p>

        {/* ── Step 0: Candidate Info ──────────────────────────────── */}
        {step === 0 && (
          <div className="space-y-6 animate-fade-in-up">
            <div className="glass rounded-2xl p-6 space-y-5">
              <h2 className="font-semibold flex items-center gap-2">
                <User size={18} className="text-brand-400" />
                Candidate Information
              </h2>

              <div>
                <label className="block text-sm text-white/50 mb-1.5">Full Name *</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  className="w-full px-4 py-3 rounded-xl bg-surface-800 border border-white/5 text-white placeholder:text-white/20 focus:outline-none focus:border-brand-500/50 transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm text-white/50 mb-1.5">Email</label>
                <input
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="john@example.com"
                  className="w-full px-4 py-3 rounded-xl bg-surface-800 border border-white/5 text-white placeholder:text-white/20 focus:outline-none focus:border-brand-500/50 transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm text-white/50 mb-1.5">
                  <Briefcase size={14} className="inline mr-1" />
                  Target Role
                </label>
                <input
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  placeholder="ML Engineer, Backend Developer, etc."
                  className="w-full px-4 py-3 rounded-xl bg-surface-800 border border-white/5 text-white placeholder:text-white/20 focus:outline-none focus:border-brand-500/50 transition-colors"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-white/50 mb-1.5">
                    <GraduationCap size={14} className="inline mr-1" />
                    Experience (Years)
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={30}
                    value={experience}
                    onChange={(e) => setExperience(Number(e.target.value))}
                    className="w-full px-4 py-3 rounded-xl bg-surface-800 border border-white/5 text-white focus:outline-none focus:border-brand-500/50 transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-sm text-white/50 mb-1.5">
                    Skills (comma-separated)
                  </label>
                  <input
                    value={skills}
                    onChange={(e) => setSkills(e.target.value)}
                    placeholder="python, ml, react"
                    className="w-full px-4 py-3 rounded-xl bg-surface-800 border border-white/5 text-white placeholder:text-white/20 focus:outline-none focus:border-brand-500/50 transition-colors"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={() => setStep(1)}
              disabled={!name.trim()}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Continue
              <ArrowRight size={18} />
            </button>
          </div>
        )}

        {/* ── Step 1: Interview Config ───────────────────────────── */}
        {step === 1 && (
          <div className="space-y-6 animate-fade-in-up">
            {/* Interview Type */}
            <div className="glass rounded-2xl p-6 space-y-4">
              <h2 className="font-semibold flex items-center gap-2">
                <Layers size={18} className="text-brand-400" />
                Interview Type
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {interviewTypes.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setInterviewType(t.id)}
                    className={`p-4 rounded-xl text-left transition-all duration-200 ${
                      interviewType === t.id
                        ? "glass-light ring-2 ring-brand-500/50 scale-[1.02]"
                        : "bg-surface-800/50 border border-white/5 hover:border-white/10"
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-1.5">
                      <div
                        className={`w-8 h-8 rounded-lg bg-gradient-to-br ${t.color} flex items-center justify-center`}
                      >
                        <t.icon size={16} className="text-white" />
                      </div>
                      <span className="font-medium text-sm">{t.label}</span>
                    </div>
                    <p className="text-xs text-white/35 pl-11">{t.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Difficulty */}
            <div className="glass rounded-2xl p-6 space-y-4">
              <h2 className="font-semibold flex items-center gap-2">
                <Gauge size={18} className="text-brand-400" />
                Starting Difficulty
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {difficulties.map((d) => (
                  <button
                    key={d.id}
                    onClick={() => setDifficulty(d.id)}
                    className={`p-3 rounded-xl text-center transition-all duration-200 ${
                      difficulty === d.id
                        ? "glass-light ring-2 ring-brand-500/50"
                        : "bg-surface-800/50 border border-white/5 hover:border-white/10"
                    }`}
                  >
                    <div className={`font-semibold text-sm ${d.color}`}>{d.label}</div>
                    <div className="text-xs text-white/30 mt-0.5">{d.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Persona */}
            <div className="glass rounded-2xl p-6 space-y-4">
              <h2 className="font-semibold flex items-center gap-2">
                <User size={18} className="text-brand-400" />
                Interviewer Persona
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {personas.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setPersona(p.id)}
                    className={`p-4 rounded-xl text-left transition-all duration-200 ${
                      persona === p.id
                        ? "glass-light ring-2 ring-brand-500/50 scale-[1.02]"
                        : "bg-surface-800/50 border border-white/5 hover:border-white/10"
                    }`}
                  >
                    <div className="font-semibold text-sm text-white mb-1">{p.label}</div>
                    <div className="text-xs text-white/40">{p.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Number of Questions */}
            <div className="glass rounded-2xl p-6 space-y-3">
              <h2 className="font-semibold">Number of Questions</h2>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min={3}
                  max={20}
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(Number(e.target.value))}
                  className="flex-1 accent-brand-500"
                />
                <span className="text-2xl font-bold gradient-text w-12 text-right">
                  {numQuestions}
                </span>
              </div>
            </div>

            {error && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
                {error}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setStep(0)}
                className="flex-1 py-3.5 rounded-xl glass-light text-white/70 font-medium hover:text-white transition-colors"
              >
                Back
              </button>
              <button
                onClick={handleStart}
                disabled={loading}
                className="flex-[2] py-3.5 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    Start Interview
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
