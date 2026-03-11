"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
  Brain,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Code2,
  Zap,
  ArrowLeft,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  BarChart3,
} from "lucide-react";
import {
  getCodingQuestions,
  getCodingQuestion,
  executeCode,
  evaluateCode,
  type CodingQuestion,
  type CodeEvaluationResult,
  type ExecutionResult,
} from "@/lib/api";

// Dynamically import Monaco to avoid SSR issues
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

const LANGUAGES = [
  { id: "python", label: "Python" },
  { id: "javascript", label: "JavaScript" },
];

const diffColor: Record<string, string> = {
  easy: "text-emerald-400 bg-emerald-400/10",
  medium: "text-amber-400 bg-amber-400/10",
  hard: "text-rose-400 bg-rose-400/10",
};

export default function CodingPracticePage() {
  const [questionList, setQuestionList] = useState<{ id: string; title: string; difficulty: string; topics: string[] }[]>([]);
  const [question, setQuestion] = useState<CodingQuestion | null>(null);
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [output, setOutput] = useState<ExecutionResult | null>(null);
  const [evaluation, setEvaluation] = useState<CodeEvaluationResult | null>(null);
  const [running, setRunning] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [showPanel, setShowPanel] = useState<"output" | "evaluation" | null>(null);
  const [expandedTest, setExpandedTest] = useState<number | null>(null);
  const [error, setError] = useState("");

  // Load question list
  useEffect(() => {
    getCodingQuestions().then(setQuestionList).catch(() => {});
  }, []);

  // Load specific question
  const loadQuestion = async (id: string) => {
    try {
      const q = await getCodingQuestion(id, language);
      setQuestion(q);
      setCode(q.starter_code);
      setOutput(null);
      setEvaluation(null);
      setShowPanel(null);
      setError("");
    } catch {
      setError("Failed to load question.");
    }
  };

  // Change language → reload starter code
  const changeLanguage = async (lang: string) => {
    setLanguage(lang);
    if (question) {
      try {
        const q = await getCodingQuestion(question.id, lang);
        setCode(q.starter_code);
        setQuestion(q);
        setOutput(null);
        setEvaluation(null);
      } catch {}
    }
  };

  // Run code
  const handleRun = async () => {
    setRunning(true);
    setError("");
    try {
      const result = await executeCode(code, language);
      setOutput(result);
      setShowPanel("output");
    } catch {
      setError("Execution failed. Is the backend running?");
    } finally {
      setRunning(false);
    }
  };

  // Full evaluate
  const handleEvaluate = async () => {
    if (!question) return;
    setEvaluating(true);
    setError("");
    try {
      const result = await evaluateCode(question.id, code, language);
      setEvaluation(result);
      setShowPanel("evaluation");
    } catch {
      setError("Evaluation failed. Is the backend running?");
    } finally {
      setEvaluating(false);
    }
  };

  const scoreColor = (s: number, max: number) => {
    const pct = s / max;
    if (pct >= 0.8) return "score-excellent";
    if (pct >= 0.6) return "score-good";
    if (pct >= 0.4) return "score-average";
    return "score-poor";
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 glass">
        <div className="max-w-[1600px] mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
              <Brain size={16} className="text-white" />
            </div>
            <span className="font-semibold text-sm">
              Interview<span className="gradient-text">AI</span>
            </span>
          </Link>
          <div className="flex items-center gap-3 text-sm">
            <Link
              href="/dashboard"
              className="text-white/40 hover:text-white/70 transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/interview/new"
              className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 text-white text-xs font-medium hover:opacity-90 transition-opacity"
            >
              Full Interview
            </Link>
          </div>
        </div>
      </nav>

      <div className="flex-1 flex">
        {/* ── Left: Question Panel ──────────────────────────────────── */}
        <aside className="w-[380px] shrink-0 border-r border-white/5 overflow-y-auto">
          <div className="p-5">
            <Link
              href="/"
              className="inline-flex items-center gap-1 text-xs text-white/30 hover:text-white/60 transition-colors mb-4"
            >
              <ArrowLeft size={12} />
              Home
            </Link>

            <h1 className="text-lg font-bold mb-1">
              <Code2 size={18} className="inline mr-1.5 text-brand-400" />
              Coding <span className="gradient-text">Practice</span>
            </h1>
            <p className="text-xs text-white/40 mb-5">Select a problem and solve it in the editor.</p>

            {/* Question List */}
            <div className="space-y-2 mb-6">
              {questionList.map((q) => (
                <button
                  key={q.id}
                  onClick={() => loadQuestion(q.id)}
                  className={`w-full text-left p-3 rounded-xl transition-all ${
                    question?.id === q.id
                      ? "glass-light ring-1 ring-brand-500/40"
                      : "bg-surface-800/40 border border-white/5 hover:border-white/10"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{q.title}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${diffColor[q.difficulty] || ""}`}>
                      {q.difficulty}
                    </span>
                  </div>
                  <div className="flex gap-1.5 mt-1.5">
                    {q.topics.map((t) => (
                      <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-white/30">
                        {t.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </button>
              ))}
            </div>

            {/* Question Description */}
            {question && (
              <div className="glass rounded-xl p-4 animate-fade-in-up">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="font-semibold text-sm">{question.title}</h2>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${diffColor[question.difficulty] || ""}`}>
                    {question.difficulty}
                  </span>
                </div>
                <div
                  className="text-xs text-white/50 leading-relaxed prose prose-invert prose-xs max-w-none"
                  dangerouslySetInnerHTML={{
                    __html: question.description
                      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                      .replace(/`(.*?)`/g, '<code class="text-brand-300 bg-brand-500/10 px-1 rounded">$1</code>')
                      .replace(/```\n?([\s\S]*?)```/g, '<pre class="bg-surface-800 rounded-lg p-2 mt-2 mb-2 text-[11px]"><code>$1</code></pre>')
                      .replace(/\n/g, "<br/>"),
                  }}
                />
                <div className="flex items-center gap-3 mt-3 pt-3 border-t border-white/5 text-xs text-white/30">
                  <span>Tests: {question.num_test_cases}</span>
                  <span>Optimal: {question.optimal_complexity.time} / {question.optimal_complexity.space}</span>
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* ── Right: Editor + Results ───────────────────────────────── */}
        <div className="flex-1 flex flex-col">
          {!question ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Code2 size={48} className="text-white/10 mx-auto mb-3" />
                <p className="text-white/30 text-sm">Select a problem from the left panel.</p>
              </div>
            </div>
          ) : (
            <>
              {/* Toolbar */}
              <div className="h-12 flex items-center justify-between px-4 border-b border-white/5 glass">
                <div className="flex items-center gap-3">
                  {LANGUAGES.map((l) => (
                    <button
                      key={l.id}
                      onClick={() => changeLanguage(l.id)}
                      className={`px-3 py-1 rounded-lg text-xs transition-colors ${
                        language === l.id ? "bg-brand-500/20 text-brand-300" : "text-white/30 hover:text-white/50"
                      }`}
                    >
                      {l.label}
                    </button>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleRun}
                    disabled={running || evaluating}
                    className="px-4 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-medium flex items-center gap-1.5 hover:bg-emerald-500 transition-colors disabled:opacity-40"
                  >
                    {running ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                    Run
                  </button>
                  <button
                    onClick={handleEvaluate}
                    disabled={running || evaluating}
                    className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 text-white text-xs font-medium flex items-center gap-1.5 hover:opacity-90 transition-opacity disabled:opacity-40"
                  >
                    {evaluating ? <Loader2 size={12} className="animate-spin" /> : <Zap size={12} />}
                    Evaluate
                  </button>
                </div>
              </div>

              {/* Editor */}
              <div className="flex-1 min-h-0">
                <MonacoEditor
                  height="100%"
                  language={language}
                  value={code}
                  onChange={(v) => setCode(v || "")}
                  theme="vs-dark"
                  options={{
                    fontSize: 14,
                    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                    minimap: { enabled: false },
                    padding: { top: 16 },
                    lineNumbers: "on",
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    smoothScrolling: true,
                    cursorSmoothCaretAnimation: "on",
                  }}
                />
              </div>

              {/* ── Results Panel ───────────────────────────────────── */}
              {(showPanel || error) && (
                <div className="h-[280px] border-t border-white/5 overflow-y-auto bg-surface-900/80">
                  <div className="p-4">
                    {error && (
                      <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm mb-3">
                        <AlertCircle size={14} className="inline mr-1.5" />
                        {error}
                      </div>
                    )}

                    {/* Output */}
                    {showPanel === "output" && output && (
                      <div className="animate-fade-in-up">
                        <div className="flex items-center gap-2 mb-3">
                          {output.success ? (
                            <CheckCircle2 size={16} className="text-emerald-400" />
                          ) : (
                            <XCircle size={16} className="text-red-400" />
                          )}
                          <span className="text-sm font-medium">
                            {output.success ? "Success" : "Error"}
                          </span>
                          <span className="text-xs text-white/30 ml-auto flex items-center gap-1">
                            <Clock size={10} />
                            {output.execution_time_ms}ms
                          </span>
                        </div>
                        {output.stdout && (
                          <pre className="p-3 rounded-lg bg-surface-800 text-xs text-white/70 font-mono whitespace-pre-wrap mb-2">
                            {output.stdout}
                          </pre>
                        )}
                        {output.stderr && (
                          <pre className="p-3 rounded-lg bg-red-500/5 border border-red-500/10 text-xs text-red-300/80 font-mono whitespace-pre-wrap">
                            {output.stderr}
                          </pre>
                        )}
                        {output.error && (
                          <pre className="p-3 rounded-lg bg-red-500/5 border border-red-500/10 text-xs text-red-300/80 font-mono">
                            {output.error}
                          </pre>
                        )}
                      </div>
                    )}

                    {/* Evaluation */}
                    {showPanel === "evaluation" && evaluation && (
                      <div className="animate-fade-in-up space-y-4">
                        {/* Summary Row */}
                        <div className="flex items-center gap-4">
                          <div className="text-center">
                            <div className={`text-3xl font-extrabold ${scoreColor(evaluation.review.overall_code_score, 10)}`}>
                              {evaluation.review.overall_code_score.toFixed(1)}
                              <span className="text-sm text-white/30">/10</span>
                            </div>
                            <div className="text-[10px] text-white/30 mt-0.5">Overall</div>
                          </div>

                          <div className="flex-1 grid grid-cols-4 gap-2">
                            {[
                              { label: "Quality", val: evaluation.review.code_quality_score },
                              { label: "Correct", val: evaluation.review.correctness_score },
                              { label: "Efficient", val: evaluation.review.efficiency_score },
                              { label: "Style", val: evaluation.review.style_score },
                            ].map((s) => (
                              <div key={s.label} className="text-center">
                                <div className={`text-sm font-bold ${scoreColor(s.val, 5)}`}>
                                  {s.val.toFixed(1)}<span className="text-[10px] text-white/30">/5</span>
                                </div>
                                <div className="text-[10px] text-white/30">{s.label}</div>
                              </div>
                            ))}
                          </div>

                          <div className="text-center shrink-0">
                            <div className="flex items-center gap-1 text-sm">
                              <BarChart3 size={14} className="text-brand-400" />
                              <span className="font-medium">{evaluation.test_results.passed}/{evaluation.test_results.total_tests}</span>
                            </div>
                            <div className="text-[10px] text-white/30">Tests</div>
                          </div>
                        </div>

                        {/* Complexity */}
                        <div className="flex items-center gap-4 text-xs">
                          <span className="text-white/40">Complexity:</span>
                          <span className={`font-mono ${evaluation.complexity.time === evaluation.optimal_complexity.time ? "text-emerald-400" : "text-amber-400"}`}>
                            Time {evaluation.complexity.time}
                          </span>
                          <span className={`font-mono ${evaluation.complexity.space === evaluation.optimal_complexity.space ? "text-emerald-400" : "text-amber-400"}`}>
                            Space {evaluation.complexity.space}
                          </span>
                          <span className="text-white/20">|</span>
                          <span className="text-white/30">
                            Optimal: {evaluation.optimal_complexity.time} / {evaluation.optimal_complexity.space}
                          </span>
                        </div>

                        {/* Test Results */}
                        <div className="space-y-1.5">
                          {evaluation.test_results.results.map((t) => (
                            <div key={t.test_index}>
                              <button
                                onClick={() => setExpandedTest(expandedTest === t.test_index ? null : t.test_index)}
                                className="w-full flex items-center gap-2 p-2 rounded-lg bg-surface-800/50 hover:bg-surface-800 transition-colors text-xs"
                              >
                                {t.passed ? (
                                  <CheckCircle2 size={14} className="text-emerald-400" />
                                ) : (
                                  <XCircle size={14} className="text-red-400" />
                                )}
                                <span className="text-white/60">Test {t.test_index + 1}</span>
                                <span className="text-white/20 ml-auto flex items-center gap-1">
                                  <Clock size={10} />
                                  {t.execution_time_ms}ms
                                </span>
                                {expandedTest === t.test_index ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                              </button>
                              {expandedTest === t.test_index && (
                                <div className="mt-1 p-2 rounded-lg bg-surface-800/30 space-y-1 text-[11px] font-mono">
                                  <div><span className="text-white/30">Input:</span> <span className="text-white/60">{JSON.stringify(t.input)}</span></div>
                                  <div><span className="text-white/30">Expected:</span> <span className="text-emerald-400/70">{JSON.stringify(t.expected)}</span></div>
                                  <div><span className="text-white/30">Actual:</span> <span className={t.passed ? "text-emerald-400/70" : "text-red-400/70"}>{t.actual !== null ? String(t.actual) : t.error || "N/A"}</span></div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>

                        {/* Feedback */}
                        <p className="text-xs text-white/50 leading-relaxed">{evaluation.review.feedback}</p>

                        {evaluation.review.strengths.length > 0 && (
                          <div>
                            <span className="text-xs font-medium text-emerald-400">Strengths:</span>
                            <ul className="mt-1 space-y-0.5">
                              {evaluation.review.strengths.map((s, i) => (
                                <li key={i} className="text-xs text-white/40 flex items-start gap-1.5">
                                  <CheckCircle2 size={10} className="text-emerald-400 mt-0.5 shrink-0" />
                                  {s}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {evaluation.review.suggestions.length > 0 && (
                          <div>
                            <span className="text-xs font-medium text-amber-400">Suggestions:</span>
                            <ul className="mt-1 space-y-0.5">
                              {evaluation.review.suggestions.map((s, i) => (
                                <li key={i} className="text-xs text-white/40 flex items-start gap-1.5">
                                  <Zap size={10} className="text-amber-400 mt-0.5 shrink-0" />
                                  {s}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
