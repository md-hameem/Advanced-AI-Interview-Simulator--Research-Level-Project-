"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  Brain,
  ArrowLeft,
  Award,
  CheckCircle2,
  AlertCircle,
  BookOpen,
  Download,
  TrendingUp,
  Loader2,
} from "lucide-react";
import { getReport, type Report } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function ReportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: interviewId } = use(params);
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const r = await getReport(interviewId);
        setReport(r);
      } catch {
        setError("Failed to load report. Make sure the interview is completed.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [interviewId]);

  const scoreColor = (score: number, max: number) => {
    const pct = score / max;
    if (pct >= 0.8) return "score-excellent";
    if (pct >= 0.6) return "score-good";
    if (pct >= 0.4) return "score-average";
    return "score-poor";
  };

  const recBadge = (rec: string) => {
    if (rec.includes("strong_hire")) return { text: "STRONG HIRE", cls: "bg-emerald-500/15 text-emerald-400 ring-emerald-500/20" };
    if (rec.includes("hire") && !rec.includes("no")) return { text: "HIRE", cls: "bg-green-500/15 text-green-400 ring-green-500/20" };
    if (rec.includes("lean_no")) return { text: "LEAN NO HIRE", cls: "bg-amber-500/15 text-amber-400 ring-amber-500/20" };
    return { text: "NO HIRE", cls: "bg-red-500/15 text-red-400 ring-red-500/20" };
  };

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      const res = await fetch(`${API_BASE}/interviews/${interviewId}/report/pdf`);
      if (!res.ok) throw new Error("PDF generation failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `interview_report_${interviewId.slice(0, 8)}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      alert("Failed to download PDF. Is the backend running?");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center mx-auto mb-4 animate-pulse-glow">
            <Brain size={22} className="text-white" />
          </div>
          <p className="text-white/40">Generating report...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="glass rounded-2xl p-8 text-center max-w-md">
          <AlertCircle size={40} className="text-red-400 mx-auto mb-4" />
          <p className="text-white/60 mb-4">{error || "Report not available."}</p>
          <Link href="/" className="text-brand-400 hover:underline text-sm">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  const badge = recBadge(report.recommendation);

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

      <div className="max-w-3xl mx-auto pt-28 pb-16 px-6">
        <Link
          href="/"
          className="inline-flex items-center gap-1 text-sm text-white/40 hover:text-white/70 transition-colors mb-6"
        >
          <ArrowLeft size={16} />
          Back
        </Link>

        {/* Header */}
        <div className="glass rounded-2xl p-8 mb-6 text-center animate-fade-in-up">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center mx-auto mb-4">
            <Award size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold mb-1">Candidate Assessment Report</h1>
          <p className="text-white/40 text-sm mb-4">
            {report.candidate_name} — {report.target_role || "Software Engineer"} ({report.interview_type})
          </p>
          <span className={`inline-block px-4 py-1.5 rounded-full text-sm font-bold ring-1 ${badge.cls}`}>
            {badge.text}
          </span>
        </div>

        {/* Overall Score */}
        <div className="glass rounded-2xl p-6 mb-6 animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          <div className="text-center mb-6">
            <div className={`text-6xl font-extrabold ${scoreColor(report.overall_score, 10)}`}>
              {report.overall_score.toFixed(1)}
              <span className="text-xl text-white/30">/10</span>
            </div>
            <p className="text-sm text-white/40 mt-1">Overall Performance</p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {[
              { label: "Technical", score: report.technical_score, max: 5 },
              { label: "Communication", score: report.communication_score, max: 5 },
              { label: "Problem Solving", score: report.problem_solving_score, max: 5 },
            ].map((s) => (
              <div key={s.label} className="text-center">
                <div className={`text-2xl font-bold ${scoreColor(s.score, s.max)}`}>
                  {s.score.toFixed(1)}
                  <span className="text-sm text-white/30">/{s.max}</span>
                </div>
                <div className="text-xs text-white/40 mt-1">{s.label}</div>
                <div className="h-1.5 bg-surface-800 rounded-full mt-2 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-brand-500 to-brand-400"
                    style={{ width: `${(s.score / s.max) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Strengths & Weaknesses */}
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="glass rounded-2xl p-6 animate-fade-in-up" style={{ animationDelay: "0.15s" }}>
            <h3 className="font-semibold flex items-center gap-2 text-emerald-400 mb-3">
              <CheckCircle2 size={18} />
              Strengths
            </h3>
            <ul className="space-y-2">
              {report.strengths.map((s, i) => (
                <li key={i} className="text-sm text-white/60 flex items-start gap-2">
                  <span className="text-emerald-400 mt-1">•</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>

          <div className="glass rounded-2xl p-6 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
            <h3 className="font-semibold flex items-center gap-2 text-amber-400 mb-3">
              <TrendingUp size={18} />
              Areas for Improvement
            </h3>
            <ul className="space-y-2">
              {report.weaknesses.map((w, i) => (
                <li key={i} className="text-sm text-white/60 flex items-start gap-2">
                  <span className="text-amber-400 mt-1">•</span>
                  {w}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Detailed Feedback */}
        <div className="glass rounded-2xl p-6 mb-6 animate-fade-in-up" style={{ animationDelay: "0.25s" }}>
          <h3 className="font-semibold mb-3">Detailed Feedback</h3>
          <p className="text-sm text-white/50 leading-relaxed whitespace-pre-line">
            {report.detailed_feedback}
          </p>
        </div>

        {/* Question-by-Question Breakdown */}
        <div className="glass rounded-2xl p-6 mb-6 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <BookOpen size={18} className="text-brand-400" />
            Question Scores ({report.questions_answered} / {report.total_questions})
          </h3>
          <div className="space-y-3">
            {report.question_scores.map((q, i) => (
              <div key={i} className="p-3 rounded-xl bg-surface-800/50 border border-white/5">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <p className="text-sm text-white/70 flex-1 line-clamp-2">
                    <span className="text-white/30 mr-1">Q{i + 1}.</span>
                    {q.question}
                  </p>
                  <span className={`text-lg font-bold shrink-0 ${scoreColor(q.score, 10)}`}>
                    {q.score.toFixed(1)}
                  </span>
                </div>
                <div className="flex gap-3 text-xs text-white/30">
                  <span>Correctness: {q.correctness}/5</span>
                  <span>Depth: {q.depth}/5</span>
                  <span>Clarity: {q.clarity}/5</span>
                  <span>Reasoning: {q.reasoning}/5</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Study Recommendations */}
        {report.study_recommendations && report.study_recommendations.length > 0 && (
          <div className="glass rounded-2xl p-6 mb-6 animate-fade-in-up" style={{ animationDelay: "0.35s" }}>
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <BookOpen size={18} className="text-brand-400" />
              Recommended Study Topics
            </h3>
            <div className="flex flex-wrap gap-2">
              {report.study_recommendations.map((topic, i) => (
                <span
                  key={i}
                  className="px-3 py-1.5 rounded-full text-xs bg-brand-500/10 text-brand-300 border border-brand-500/15"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
          <button
            onClick={handleDownloadPDF}
            disabled={downloading}
            className="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-60"
          >
            {downloading ? <Loader2 size={18} className="animate-spin" /> : <Download size={18} />}
            {downloading ? "Generating..." : "Download PDF"}
          </button>
          <Link
            href={`/dashboard/learning-plan?interviewId=${report.interview_id}`}
            className="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
          >
            <BookOpen size={18} />
            View Learning Plan
          </Link>
          <Link
            href="/interview/new"
            className="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold text-center hover:opacity-90 transition-opacity"
          >
            New Interview
          </Link>
          <Link
            href="/dashboard"
            className="flex-1 py-3.5 rounded-xl glass-light text-white/70 font-medium text-center hover:text-white transition-colors"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
