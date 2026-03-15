"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Brain,
  ArrowLeft,
  BookOpen,
  CheckCircle2,
  Calendar,
  AlertCircle,
  Lightbulb,
} from "lucide-react";
import { getLearningPlan, getCandidates, type Candidate } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface LearningPlan {
  candidate_id: string;
  plan: string;
  generated_at: string;
}

function LearningPlanContent() {
  const searchParams = useSearchParams();
  const interviewId = searchParams.get("interviewId");

  const [plan, setPlan] = useState<LearningPlan | null>(null);
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      if (!interviewId) {
        setError("No interview ID provided.");
        setLoading(false);
        return;
      }
      try {
        const { getInterview } = await import("@/lib/api");
        const interview = await getInterview(interviewId);
        
        const [planData, allCandidates] = await Promise.all([
          getLearningPlan(interview.candidate_id),
          getCandidates(),
        ]);
        setPlan(planData);
        setCandidate(allCandidates.find((c) => c.id === interview.candidate_id) || null);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Failed to fetch learning plan. Ensure Candidate has a completed interview.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [interviewId]);

  if (loading) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center mx-auto mb-6 animate-pulse-glow">
          <Brain size={32} className="text-white" />
        </div>
        <div className="text-xl font-semibold mb-2">Architecting Learning Plan...</div>
        <p className="text-white/40">Analyzing your interview data to build a custom study guide.</p>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="glass rounded-2xl p-8 text-center max-w-md">
          <AlertCircle size={40} className="text-red-400 mx-auto mb-4" />
          <p className="text-white/60 mb-4">{error}</p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-surface-800 text-white hover:bg-surface-700 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="max-w-4xl mx-auto"
    >
      <Link
        href="/dashboard"
        className="inline-flex items-center gap-1 text-sm text-white/40 hover:text-white/70 transition-colors mb-6"
      >
        <ArrowLeft size={16} />
        Dashboard
      </Link>

      {/* Header Profile Card */}
      <div className="glass rounded-3xl p-8 mb-8 relative overflow-hidden">
        {/* Decorative background blur */}
        <div className="absolute -top-32 -right-32 w-64 h-64 bg-emerald-500/20 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-brand-500/20 rounded-full blur-[100px] pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 to-brand-600 flex items-center justify-center shrink-0 shadow-lg shadow-brand-500/25">
              <BookOpen size={28} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold mb-1">
                Personalized Learning Plan
              </h1>
              <div className="text-white/60 text-sm flex items-center gap-2">
                <span className="font-semibold text-white/90">
                  {candidate?.name || "Candidate"}
                </span>
                <span>•</span>
                <span>{candidate?.target_role || "General Training"}</span>
                <span>•</span>
                <span>Generated {new Date(plan.generated_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
          <div className="shrink-0 flex items-center gap-2 bg-white/5 border border-white/10 px-4 py-2 rounded-xl text-sm">
            <CheckCircle2 size={16} className="text-emerald-400" />
            <span className="text-white/80">AI Optimized</span>
          </div>
        </div>
      </div>

      {/* Markdown Content rendered via ReactMarkdown with custom components for glassmorphism */}
      <div className="glass rounded-3xl p-8 mb-8 prose prose-invert prose-brand max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ node, ...props }) => (
              <h1 className="text-3xl font-extrabold pb-4 border-b border-white/10 mb-6 gradient-text" {...props} />
            ),
            h2: ({ node, ...props }) => (
              <h2 className="text-2xl font-bold mt-10 mb-6 flex items-center gap-2 text-white/90" {...props} />
            ),
            h3: ({ node, ...props }) => (
              <h3 className="text-xl font-semibold mt-8 mb-4 text-emerald-400" {...props} />
            ),
            ul: ({ node, ...props }) => (
              <ul className="space-y-3 my-6 pl-4" {...props} />
            ),
             li: ({ node, ...props }) => (
              <li className="flex items-start gap-2 text-white/70" {...props}>
                <span className="shrink-0 w-1.5 h-1.5 rounded-full bg-brand-500 mt-2.5 mr-2" />
                <span className="flex-1">{props.children}</span>
              </li>
            ),
            strong: ({ node, ...props }) => (
              <strong className="text-white font-semibold" {...props} />
            ),
            a: ({ node, ...props }) => (
              <a className="text-brand-400 hover:text-brand-300 underline decoration-white/20 underline-offset-4 transition-colors" {...props} />
            ),
            blockquote: ({ node, ...props }) => (
               <blockquote className="border-l-4 border-brand-500 bg-brand-500/5 py-2 pr-4 pl-5 rounded-r-xl italic my-6 text-white/80" {...props} />
            )
          }}
        >
          {plan.plan}
        </ReactMarkdown>
      </div>

      <div className="flex justify-center pb-20">
         <div className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl glass-light text-white/60 text-sm">
           <Lightbulb size={16} className="text-amber-400" />
           Complete this plan and take another mock interview to track progress.
         </div>
      </div>
    </motion.div>
  );
}

export default function LearningPlanPage() {
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
             href="/dashboard"
             className="px-4 py-2 text-sm font-medium rounded-xl glass-light text-white/80 hover:text-white transition-colors"
          >
             Dashboard
          </Link>
        </div>
      </nav>

      <div className="pt-28 px-6">
        <Suspense fallback={<div className="text-center mt-20 text-white/50">Loading plan layout...</div>}>
          <LearningPlanContent />
        </Suspense>
      </div>
    </div>
  );
}
