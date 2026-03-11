"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Brain,
  MessageSquare,
  Send,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowLeft,
  Star,
  Users,
  Shield,
  Lightbulb,
  Target,
  Zap,
} from "lucide-react";
import {
  getBehavioralQuestions,
  analyzeBehavioral,
  type BehavioralResult,
} from "@/lib/api";

const competencyIcons: Record<string, typeof Users> = {
  leadership: Shield,
  teamwork: Users,
  conflict_resolution: Zap,
  problem_solving: Lightbulb,
  communication: MessageSquare,
  adaptability: Star,
  ownership: Target,
  initiative: Zap,
  time_management: Star,
  mentoring: Users,
};

const competencyColors: Record<string, string> = {
  leadership: "from-violet-500 to-purple-600",
  teamwork: "from-cyan-500 to-blue-600",
  conflict_resolution: "from-amber-500 to-orange-600",
  problem_solving: "from-emerald-500 to-green-600",
  communication: "from-pink-500 to-rose-600",
  adaptability: "from-sky-500 to-indigo-600",
  ownership: "from-amber-500 to-yellow-600",
  initiative: "from-teal-500 to-cyan-600",
};

const starColors: Record<string, string> = {
  situation: "from-blue-500 to-cyan-500",
  task: "from-violet-500 to-purple-500",
  action: "from-emerald-500 to-green-500",
  result: "from-amber-500 to-orange-500",
};

const starLabels: Record<string, string> = {
  situation: "S — Situation",
  task: "T — Task",
  action: "A — Action",
  result: "R — Result",
};

export default function BehavioralPracticePage() {
  const [questionList, setQuestionList] = useState<{ id: string; question: string; competency: string; difficulty: string }[]>([]);
  const [selectedQ, setSelectedQ] = useState<{ id: string; question: string; competency: string; difficulty: string } | null>(null);
  const [answer, setAnswer] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<BehavioralResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getBehavioralQuestions().then(setQuestionList).catch(() => {});
  }, []);

  const handleAnalyze = async () => {
    if (!selectedQ || !answer.trim()) return;
    setAnalyzing(true);
    setError("");
    try {
      const r = await analyzeBehavioral(selectedQ.id, answer.trim());
      setResult(r);
    } catch {
      setError("Analysis failed. Is the backend running?");
    } finally {
      setAnalyzing(false);
    }
  };

  const scoreColor = (s: number, max: number) => {
    const pct = s / max;
    if (pct >= 0.8) return "score-excellent";
    if (pct >= 0.6) return "score-good";
    if (pct >= 0.4) return "score-average";
    return "score-poor";
  };

  const confidenceBadge = (c: string) => {
    switch (c) {
      case "strong": return "bg-emerald-500/15 text-emerald-400";
      case "moderate": return "bg-amber-500/15 text-amber-400";
      case "weak": return "bg-orange-500/15 text-orange-400";
      default: return "bg-red-500/15 text-red-400";
    }
  };

  return (
    <div className="min-h-screen">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
              <Brain size={16} className="text-white" />
            </div>
            <span className="font-semibold text-sm">
              Interview<span className="gradient-text">AI</span>
            </span>
          </Link>
          <div className="flex items-center gap-3 text-sm">
            <Link href="/coding" className="text-white/40 hover:text-white/70 transition-colors">Coding</Link>
            <Link href="/interview/new" className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 text-white text-xs font-medium">Full Interview</Link>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto pt-24 pb-16 px-6">
        <Link href="/" className="inline-flex items-center gap-1 text-xs text-white/30 hover:text-white/60 transition-colors mb-6">
          <ArrowLeft size={12} /> Home
        </Link>

        <h1 className="text-2xl font-bold mb-1">
          <MessageSquare size={22} className="inline mr-2 text-brand-400" />
          Behavioral <span className="gradient-text">Practice</span>
        </h1>
        <p className="text-sm text-white/40 mb-8">Practice answers using the STAR method and get instant AI feedback.</p>

        {/* Question Selector */}
        <div className="grid md:grid-cols-2 gap-3 mb-8">
          {questionList.map((q) => {
            const Icon = competencyIcons[q.competency] || MessageSquare;
            const gradient = competencyColors[q.competency] || "from-brand-400 to-brand-600";
            return (
              <button
                key={q.id}
                onClick={() => { setSelectedQ(q); setResult(null); setAnswer(""); }}
                className={`text-left p-4 rounded-xl transition-all ${
                  selectedQ?.id === q.id
                    ? "glass-light ring-1 ring-brand-500/40"
                    : "bg-surface-800/40 border border-white/5 hover:border-white/10"
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center shrink-0`}>
                    <Icon size={14} className="text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm leading-relaxed line-clamp-2">{q.question}</p>
                    <div className="flex items-center gap-2 mt-1.5 text-xs text-white/30">
                      <span className="capitalize">{q.competency.replace(/_/g, " ")}</span>
                      <span>•</span>
                      <span>{q.difficulty}</span>
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Answer Area */}
        {selectedQ && !result && (
          <div className="glass rounded-2xl p-6 mb-6 animate-fade-in-up">
            <div className="mb-4">
              <h2 className="font-semibold text-sm mb-1">{selectedQ.question}</h2>
              <p className="text-xs text-white/30 capitalize">{selectedQ.competency.replace(/_/g, " ")} • {selectedQ.difficulty}</p>
            </div>

            <div className="mb-3 p-3 rounded-xl bg-brand-500/5 border border-brand-500/10 text-xs text-brand-300/70">
              <Star size={12} className="inline mr-1" />
              <strong>STAR Tip:</strong> Structure your answer with <strong>S</strong>ituation → <strong>T</strong>ask → <strong>A</strong>ction → <strong>R</strong>esult for the best score.
            </div>

            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Describe a specific situation using the STAR method..."
              rows={8}
              className="w-full px-4 py-3 rounded-xl bg-surface-800 border border-white/5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-brand-500/50 transition-colors resize-none mb-3"
            />

            {error && (
              <p className="text-xs text-red-400 mb-3">{error}</p>
            )}

            <button
              onClick={handleAnalyze}
              disabled={!answer.trim() || analyzing}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              {analyzing ? (
                <><Loader2 size={16} className="animate-spin" /> Analyzing STAR components...</>
              ) : (
                <><Send size={16} /> Analyze Answer</>
              )}
            </button>
          </div>
        )}

        {/* ── Results ───────────────────────────────────────────── */}
        {result && (
          <div className="space-y-5 animate-fade-in-up">
            {/* Overall Score */}
            <div className="glass rounded-2xl p-6 text-center">
              <div className={`text-5xl font-extrabold ${scoreColor(result.analysis.overall_behavioral_score, 10)}`}>
                {result.analysis.overall_behavioral_score.toFixed(1)}
                <span className="text-xl text-white/30">/10</span>
              </div>
              <p className="text-sm text-white/40 mt-1">Behavioral Assessment Score</p>
              <p className="text-xs text-white/30 mt-0.5 capitalize">{result.competency.replace(/_/g, " ")}</p>
            </div>

            {/* STAR Components Visual */}
            <div className="glass rounded-2xl p-6">
              <h3 className="font-semibold text-sm mb-4 flex items-center gap-2">
                <Star size={16} className="text-brand-400" />
                STAR Framework Analysis
                <span className="ml-auto text-xs text-white/30">
                  {result.star_detection.star_completeness} components detected
                </span>
              </h3>

              <div className="grid grid-cols-2 gap-4">
                {(["situation", "task", "action", "result"] as const).map((key) => {
                  const comp = result.star_detection.components[key];
                  const analysis = result.analysis;
                  const score = key === "situation" ? analysis.situation_score
                    : key === "task" ? analysis.task_score
                    : key === "action" ? analysis.action_score
                    : analysis.result_score;
                  const summary = key === "situation" ? analysis.situation_summary
                    : key === "task" ? analysis.task_summary
                    : key === "action" ? analysis.action_summary
                    : analysis.result_summary;

                  return (
                    <div
                      key={key}
                      className={`p-4 rounded-xl border transition-all ${
                        comp.detected
                          ? "bg-surface-800/50 border-white/10"
                          : "bg-red-500/5 border-red-500/10"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className={`w-6 h-6 rounded-md bg-gradient-to-br ${starColors[key]} flex items-center justify-center`}>
                            <span className="text-white text-xs font-bold">{key[0].toUpperCase()}</span>
                          </div>
                          <span className="text-xs font-medium">{starLabels[key]}</span>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${confidenceBadge(comp.confidence)}`}>
                          {comp.confidence}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 mb-2">
                        <div className={`text-lg font-bold ${scoreColor(score, 5)}`}>
                          {score.toFixed(1)}<span className="text-xs text-white/30">/5</span>
                        </div>
                        <div className="flex-1 h-1.5 bg-surface-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full bg-gradient-to-r ${starColors[key]}`}
                            style={{ width: `${(score / 5) * 100}%` }}
                          />
                        </div>
                      </div>

                      {summary && (
                        <p className="text-xs text-white/40 leading-relaxed line-clamp-3">{summary}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Additional Scores */}
            <div className="glass rounded-2xl p-6">
              <h3 className="font-semibold text-sm mb-4">Additional Assessment</h3>
              <div className="grid grid-cols-4 gap-4">
                {[
                  { label: "Competency", val: result.analysis.competency_score },
                  { label: "Communication", val: result.analysis.communication_score },
                  { label: "Specificity", val: result.analysis.specificity_score },
                  { label: "Impact", val: result.analysis.impact_score },
                ].map((s) => (
                  <div key={s.label} className="text-center">
                    <div className={`text-xl font-bold ${scoreColor(s.val, 5)}`}>
                      {s.val.toFixed(1)}<span className="text-xs text-white/30">/5</span>
                    </div>
                    <div className="text-xs text-white/30 mt-0.5">{s.label}</div>
                    <div className="h-1.5 bg-surface-800 rounded-full mt-2 overflow-hidden">
                      <div className="h-full rounded-full bg-gradient-to-r from-brand-500 to-brand-400" style={{ width: `${(s.val / 5) * 100}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Feedback */}
            <div className="glass rounded-2xl p-6">
              <p className="text-sm text-white/50 leading-relaxed">{result.analysis.feedback}</p>
            </div>

            {/* Strengths & Improvements */}
            <div className="grid md:grid-cols-2 gap-4">
              {result.analysis.strengths.length > 0 && (
                <div className="glass rounded-2xl p-5">
                  <h4 className="text-sm font-medium text-emerald-400 mb-2 flex items-center gap-1.5">
                    <CheckCircle2 size={14} /> Strengths
                  </h4>
                  <ul className="space-y-1.5">
                    {result.analysis.strengths.map((s, i) => (
                      <li key={i} className="text-xs text-white/50 flex items-start gap-1.5">
                        <span className="text-emerald-400 mt-0.5">•</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {result.analysis.improvements.length > 0 && (
                <div className="glass rounded-2xl p-5">
                  <h4 className="text-sm font-medium text-amber-400 mb-2 flex items-center gap-1.5">
                    <AlertTriangle size={14} /> Improvements
                  </h4>
                  <ul className="space-y-1.5">
                    {result.analysis.improvements.map((s, i) => (
                      <li key={i} className="text-xs text-white/50 flex items-start gap-1.5">
                        <span className="text-amber-400 mt-0.5">•</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Red Flags */}
            {result.analysis.red_flags.length > 0 && (
              <div className="glass rounded-2xl p-5 border border-red-500/10">
                <h4 className="text-sm font-medium text-red-400 mb-2 flex items-center gap-1.5">
                  <XCircle size={14} /> Red Flags
                </h4>
                <ul className="space-y-1.5">
                  {result.analysis.red_flags.map((f, i) => (
                    <li key={i} className="text-xs text-red-300/60 flex items-start gap-1.5">
                      <span className="text-red-400 mt-0.5">•</span> {f}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Follow-ups */}
            {result.follow_up_questions.length > 0 && (
              <div className="glass rounded-2xl p-5">
                <h4 className="text-sm font-medium mb-2 flex items-center gap-1.5">
                  <MessageSquare size={14} className="text-brand-400" /> Follow-Up Questions
                </h4>
                <ul className="space-y-2">
                  {result.follow_up_questions.map((q, i) => (
                    <li key={i} className="text-sm text-white/60 p-2 rounded-lg bg-surface-800/50">{q}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Try Again */}
            <button
              onClick={() => { setResult(null); setAnswer(""); }}
              className="w-full py-3 rounded-xl glass-light text-white/60 font-medium hover:text-white transition-colors"
            >
              Try Another Answer
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
