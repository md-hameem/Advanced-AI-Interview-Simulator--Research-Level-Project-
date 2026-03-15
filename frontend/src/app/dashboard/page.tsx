"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Brain,
  Users,
  BarChart3,
  ArrowRight,
  Clock,
  Award,
  Target,
  Plus,
  TrendingUp,
} from "lucide-react";
import { motion } from "framer-motion";
import {
  getAnalyticsOverview,
  getInterviews,
  getCandidates,
  type AnalyticsOverview,
  type Interview,
  type Candidate,
} from "@/lib/api";

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [a, iv, c] = await Promise.all([
          getAnalyticsOverview(),
          getInterviews(),
          getCandidates(),
        ]);
        setAnalytics(a);
        setInterviews(iv);
        setCandidates(c);
      } catch {
        // Backend probably not running
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const scoreColor = (score: number, max: number) => {
    const pct = score / max;
    if (pct >= 0.8) return "score-excellent";
    if (pct >= 0.6) return "score-good";
    if (pct >= 0.4) return "score-average";
    return "score-poor";
  };

  const statusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-emerald-500/10 text-emerald-400";
      case "in_progress":
        return "bg-blue-500/10 text-blue-400";
      case "pending":
        return "bg-white/5 text-white/40";
      default:
        return "bg-white/5 text-white/30";
    }
  };

  const recBadge = (rec: string | null) => {
    if (!rec) return { text: "N/A", cls: "text-white/30" };
    if (rec.includes("strong_hire")) return { text: "STRONG HIRE", cls: "text-emerald-400" };
    if (rec.includes("hire") && !rec.includes("no")) return { text: "HIRE", cls: "text-green-400" };
    if (rec.includes("lean_no")) return { text: "LEAN NO HIRE", cls: "text-amber-400" };
    return { text: "NO HIRE", cls: "text-red-400" };
  };

  const getCandidateName = (id: string) =>
    candidates.find((c) => c.id === id)?.name || "Unknown";

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
          <Link
            href="/interview/new"
            className="px-4 py-2 text-sm font-medium rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white hover:opacity-90 transition-opacity flex items-center gap-1.5"
          >
            <Plus size={16} />
            New Interview
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto pt-28 pb-16 px-6">
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">Dashboard</span>
        </h1>
        <p className="text-white/40 mb-8">Interview analytics and performance overview.</p>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="glass rounded-2xl p-6 h-28 shimmer" />
            ))}
          </div>
        ) : (
          <>
            {/* Stats Cards */}
            <motion.div 
              initial="hidden"
              animate="visible"
              variants={{
                hidden: { opacity: 0 },
                visible: {
                  opacity: 1,
                  transition: { staggerChildren: 0.1 }
                }
              }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
            >
              {[
                { label: "Total Candidates", value: analytics?.total_candidates || 0, icon: Users, color: "violet" },
                { label: "Completed Interviews", value: analytics?.completed_interviews || 0, icon: BarChart3, color: "cyan" },
                { label: "Avg. Overall Score", value: (analytics?.average_scores?.overall || 0).toFixed(1), icon: TrendingUp, color: "emerald", score: analytics?.average_scores?.overall, max: 10 },
                { label: "Avg. Technical Score", value: `${(analytics?.average_scores?.technical || 0).toFixed(1)}/5`, icon: Target, color: "amber", score: analytics?.average_scores?.technical, max: 5 },
              ].map((stat, i) => (
                <motion.div
                  key={i}
                  variants={{
                    hidden: { opacity: 0, y: 20 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className="glass rounded-2xl p-6"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-10 h-10 rounded-xl bg-${stat.color}-500/10 flex items-center justify-center`}>
                      <stat.icon size={20} className={`text-${stat.color}-400`} />
                    </div>
                  </div>
                  <div className={`text-3xl font-bold ${stat.score !== undefined ? scoreColor(stat.score, stat.max!) : ""}`}>
                    {stat.value}
                  </div>
                  <div className="text-xs text-white/40 mt-0.5">{stat.label}</div>
                </motion.div>
              ))}
            </motion.div>

            {/* Recent Interviews */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-6 mb-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold flex items-center gap-2">
                  <Clock size={18} className="text-brand-400" />
                  Recent Interviews
                </h2>
              </div>

              {interviews.length === 0 ? (
                <div className="text-center py-12">
                  <Award size={40} className="text-white/10 mx-auto mb-3" />
                  <p className="text-white/30 text-sm mb-4">No interviews yet.</p>
                  <Link
                    href="/interview/new"
                    className="inline-flex items-center gap-1.5 text-sm text-brand-400 hover:text-brand-300 transition-colors"
                  >
                    Start your first interview
                    <ArrowRight size={14} />
                  </Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {interviews.slice(0, 10).map((iv) => {
                    const rec = recBadge(iv.recommendation);
                    return (
                      <Link
                        key={iv.id}
                        href={
                          iv.status === "completed"
                            ? `/interview/${iv.id}/report`
                            : iv.status === "in_progress"
                            ? `/interview/${iv.id}`
                            : `/interview/${iv.id}`
                        }
                        className="block p-4 rounded-xl bg-surface-800/50 border border-white/5 hover:border-brand-500/20 transition-all group"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div>
                              <div className="font-medium text-sm group-hover:text-brand-300 transition-colors">
                                {getCandidateName(iv.candidate_id)}
                              </div>
                              <div className="text-xs text-white/30 mt-0.5 flex items-center gap-2">
                                <span>{iv.interview_type}</span>
                                <span>•</span>
                                <span>{iv.difficulty}</span>
                                <span>•</span>
                                <span>{iv.total_questions} questions</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {iv.overall_score !== null && (
                              <span className={`font-bold ${scoreColor(iv.overall_score, 10)}`}>
                                {iv.overall_score.toFixed(1)}/10
                              </span>
                            )}
                            {iv.recommendation && (
                              <span className={`text-xs font-semibold ${rec.cls}`}>{rec.text}</span>
                            )}
                            <span className={`text-xs px-2 py-0.5 rounded-full ${statusBadge(iv.status)}`}>
                              {iv.status.replace(/_/g, " ")}
                            </span>
                            <ArrowRight size={14} className="text-white/20 group-hover:text-brand-400 transition-colors" />
                          </div>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              )}
            </motion.div>

            {/* Candidates */}
            {candidates.length > 0 && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="glass rounded-2xl p-6"
              >
                <h2 className="font-semibold flex items-center gap-2 mb-4">
                  <Users size={18} className="text-brand-400" />
                  Candidates
                </h2>
                <div className="grid md:grid-cols-2 gap-3">
                  {candidates.slice(0, 8).map((c) => (
                    <div
                      key={c.id}
                      className="p-3 rounded-xl bg-surface-800/50 border border-white/5"
                    >
                      <div className="font-medium text-sm">{c.name}</div>
                      <div className="text-xs text-white/30 mt-0.5">
                        {c.target_role || "No role specified"} • {c.experience_years}y exp
                      </div>
                      {c.skills.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {c.skills.slice(0, 5).map((s, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 rounded-full text-[10px] bg-brand-500/10 text-brand-300"
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
