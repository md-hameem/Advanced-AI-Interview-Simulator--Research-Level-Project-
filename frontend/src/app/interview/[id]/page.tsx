"use client";

import { useState, useEffect, useRef, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Brain,
  Send,
  Lightbulb,
  Clock,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Award,
  ChevronDown,
  ChevronUp,
  Loader2,
  Mic,
  MicOff,
  AudioWaveform,
  Keyboard,
} from "lucide-react";
import {
  startInterview,
  submitAnswer,
  submitSpeechAnswer,
  getHint,
  getInterview,
  type Question,
  type Evaluation,
  type Interview,
  type SpeechMetrics,
} from "@/lib/api";
import { useAudioRecorder } from "@/hooks/useAudioRecorder";

interface QAEntry {
  question: Question;
  answer: string | null;
  evaluation: Evaluation | null;
  speechMetrics?: SpeechMetrics | null;
}

export default function InterviewSessionPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: interviewId } = use(params);
  const router = useRouter();
  const answerRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const [interview, setInterview] = useState<Interview | null>(null);
  const [history, setHistory] = useState<QAEntry[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [hintText, setHintText] = useState("");
  const [hintsRemaining, setHintsRemaining] = useState(-1);
  const [expandedEval, setExpandedEval] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const [voiceMode, setVoiceMode] = useState(false);

  // Voice recording
  const {
    isRecording,
    duration: recordingDuration,
    audioBlob,
    startRecording,
    stopRecording,
    resetRecording,
    error: micError,
  } = useAudioRecorder();

  // Timer
  useEffect(() => {
    if (completed) return;
    const interval = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(interval);
  }, [completed]);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m.toString().padStart(2, "0")}:${sec.toString().padStart(2, "0")}`;
  };

  // Start interview on mount
  useEffect(() => {
    const init = async () => {
      try {
        const iv = await getInterview(interviewId);
        setInterview(iv);

        if (iv.status === "completed") {
          setCompleted(true);
          setLoading(false);
          return;
        }

        if (iv.status === "pending") {
          const firstQ = await startInterview(interviewId);
          setCurrentQuestion(firstQ);
        }
        setLoading(false);
      } catch {
        setError("Failed to load interview. Is the backend running?");
        setLoading(false);
      }
    };
    init();
  }, [interviewId]);

  // Scroll to bottom when new content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, currentQuestion]);

  // Focus textarea
  useEffect(() => {
    if (currentQuestion && answerRef.current) {
      answerRef.current.focus();
    }
  }, [currentQuestion]);

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || !currentQuestion || submitting) return;

    setSubmitting(true);
    setError("");
    setHintText("");

    try {
      const evaluation = await submitAnswer(interviewId, currentQuestion.id, answer.trim());

      setHistory((prev) => [
        ...prev,
        { question: currentQuestion, answer: answer.trim(), evaluation },
      ]);

      setAnswer("");

      if (evaluation.interview_completed) {
        setCompleted(true);
        setCurrentQuestion(null);
        const updatedIv = await getInterview(interviewId);
        setInterview(updatedIv);
      } else if (evaluation.next_question) {
        setCurrentQuestion(evaluation.next_question);
      }
    } catch {
      setError("Failed to submit answer. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitVoiceAnswer = async () => {
    if (!audioBlob || !currentQuestion || submitting) return;

    setSubmitting(true);
    setError("");
    setHintText("");

    try {
      const result = await submitSpeechAnswer(interviewId, currentQuestion.id, audioBlob);
      const speechMetrics = result.speech_metrics;
      const answerText = speechMetrics?.transcript || "[Voice answer]";

      setHistory((prev) => [
        ...prev,
        { question: currentQuestion, answer: answerText, evaluation: result, speechMetrics: speechMetrics || null },
      ]);

      resetRecording();

      if (result.interview_completed) {
        setCompleted(true);
        setCurrentQuestion(null);
        const updatedIv = await getInterview(interviewId);
        setInterview(updatedIv);
      } else if (result.next_question) {
        setCurrentQuestion(result.next_question);
      }
    } catch {
      setError("Failed to process voice answer. Try typing instead.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleGetHint = async () => {
    try {
      const h = await getHint(interviewId);
      setHintText(h.hint);
      setHintsRemaining(h.hints_remaining);
    } catch {
      /* no hints */
    }
  };

  const scoreColor = (score: number, max: number) => {
    const pct = score / max;
    if (pct >= 0.8) return "score-excellent";
    if (pct >= 0.6) return "score-good";
    if (pct >= 0.4) return "score-average";
    return "score-poor";
  };

  const difficultyColor: Record<string, string> = {
    easy: "text-emerald-400 bg-emerald-400/10",
    medium: "text-amber-400 bg-amber-400/10",
    hard: "text-orange-400 bg-orange-400/10",
    expert: "text-rose-400 bg-rose-400/10",
  };

  // ─── Loading State ────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center animate-fade-in-up">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center mx-auto mb-4 animate-pulse-glow">
            <Brain size={28} className="text-white" />
          </div>
          <div className="text-lg font-semibold mb-2">Preparing Interview...</div>
          <p className="text-white/40 text-sm">Generating your first question</p>
        </div>
      </div>
    );
  }

  // ─── Completed State ──────────────────────────────────────────────
  if (completed) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="max-w-lg w-full text-center animate-fade-in-up">
          <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-emerald-400 to-green-600 flex items-center justify-center mx-auto mb-6">
            <Award size={36} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold mb-3">Interview Complete!</h1>
          <p className="text-white/40 mb-8">
            You answered {history.length} question{history.length !== 1 ? "s" : ""} in{" "}
            {formatTime(elapsed)}.
          </p>

          {interview?.overall_score !== null && interview?.overall_score !== undefined && (
            <div className="glass rounded-2xl p-6 mb-6 space-y-3">
              <div className="text-5xl font-extrabold gradient-text">
                {interview.overall_score.toFixed(1)}
                <span className="text-xl text-white/40">/10</span>
              </div>
              <div className="grid grid-cols-3 gap-3 text-sm">
                <div>
                  <div className="text-white/40">Technical</div>
                  <div className={`font-semibold ${scoreColor(interview.technical_score || 0, 5)}`}>
                    {(interview.technical_score || 0).toFixed(1)}/5
                  </div>
                </div>
                <div>
                  <div className="text-white/40">Communication</div>
                  <div className={`font-semibold ${scoreColor(interview.communication_score || 0, 5)}`}>
                    {(interview.communication_score || 0).toFixed(1)}/5
                  </div>
                </div>
                <div>
                  <div className="text-white/40">Problem Solving</div>
                  <div className={`font-semibold ${scoreColor(interview.problem_solving_score || 0, 5)}`}>
                    {(interview.problem_solving_score || 0).toFixed(1)}/5
                  </div>
                </div>
              </div>
              {interview.recommendation && (
                <div className="pt-2 border-t border-white/5">
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                      interview.recommendation.includes("hire") && !interview.recommendation.includes("no")
                        ? "bg-emerald-500/10 text-emerald-400"
                        : "bg-red-500/10 text-red-400"
                    }`}
                  >
                    {interview.recommendation.replace(/_/g, " ").toUpperCase()}
                  </span>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-3">
            <Link
              href={`/interview/${interviewId}/report`}
              className="flex-1 py-3.5 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 text-white font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
            >
              View Full Report
              <ArrowRight size={18} />
            </Link>
            <Link
              href="/interview/new"
              className="flex-1 py-3.5 rounded-xl glass-light text-white/70 font-medium text-center hover:text-white transition-colors"
            >
              New Interview
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ─── Interview Session ────────────────────────────────────────────
  const answeredCount = history.length;
  const totalQ = interview?.total_questions || 10;
  const progress = (answeredCount / totalQ) * 100;

  return (
    <div className="min-h-screen flex flex-col">
      {/* ── Top Bar ──────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 glass">
        <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center">
              <Brain size={16} className="text-white" />
            </div>
            <span className="font-semibold text-sm">
              Interview<span className="gradient-text">AI</span>
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1.5 text-white/40">
              <Clock size={14} />
              {formatTime(elapsed)}
            </div>
            <div className="text-white/40">
              Q {answeredCount + 1} / {totalQ}
            </div>
          </div>
        </div>
        {/* Progress bar */}
        <div className="h-0.5 bg-surface-800">
          <div
            className="h-full bg-gradient-to-r from-brand-500 to-brand-400 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </header>

      {/* ── Chat Area ────────────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
          {/* History */}
          {history.map((entry, i) => (
            <div key={i} className="space-y-3 animate-fade-in-up">
              {/* Question bubble */}
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Brain size={14} className="text-white" />
                </div>
                <div className="glass rounded-2xl rounded-tl-md p-4 max-w-[85%]">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${difficultyColor[entry.question.difficulty] || ""}`}
                    >
                      {entry.question.difficulty}
                    </span>
                    <span className="text-xs text-white/30">{entry.question.question_type}</span>
                    {entry.question.is_follow_up === 1 && (
                      <span className="text-xs text-brand-400">follow-up</span>
                    )}
                  </div>
                  <p className="text-sm leading-relaxed">{entry.question.question_text}</p>
                </div>
              </div>

              {/* Answer bubble */}
              {entry.answer && (
                <div className="flex justify-end">
                  <div className="bg-brand-600/20 border border-brand-500/10 rounded-2xl rounded-tr-md p-4 max-w-[85%]">
                    {entry.speechMetrics && (
                      <div className="flex items-center gap-2 mb-2 text-xs text-cyan-400/60">
                        <AudioWaveform size={12} />
                        <span>Voice</span>
                        <span className="text-white/20">•</span>
                        <span>{entry.speechMetrics.words_per_minute} WPM</span>
                        <span className="text-white/20">•</span>
                        <span>Confidence: {Math.round(entry.speechMetrics.confidence_score * 100)}%</span>
                        {entry.speechMetrics.filler_word_count > 0 && (
                          <>
                            <span className="text-white/20">•</span>
                            <span className="text-amber-400/60">{entry.speechMetrics.filler_word_count} fillers</span>
                          </>
                        )}
                      </div>
                    )}
                    <p className="text-sm leading-relaxed text-white/80">{entry.answer}</p>
                  </div>
                </div>
              )}

              {/* Evaluation */}
              {entry.evaluation && (
                <div className="ml-11">
                  <button
                    onClick={() =>
                      setExpandedEval(expandedEval === entry.question.id ? null : entry.question.id)
                    }
                    className="flex items-center gap-2 text-xs text-white/40 hover:text-white/60 transition-colors"
                  >
                    <div className={`font-semibold text-sm ${scoreColor(entry.evaluation.overall_question_score, 10)}`}>
                      {entry.evaluation.overall_question_score.toFixed(1)}/10
                    </div>
                    <span>Evaluation</span>
                    {expandedEval === entry.question.id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  </button>

                  {expandedEval === entry.question.id && (
                    <div className="mt-2 glass rounded-xl p-4 space-y-3 animate-fade-in-up text-sm">
                      {/* Score bars */}
                      <div className="grid grid-cols-2 gap-3">
                        {[
                          { label: "Correctness", val: entry.evaluation.correctness_score },
                          { label: "Depth", val: entry.evaluation.depth_score },
                          { label: "Clarity", val: entry.evaluation.clarity_score },
                          { label: "Reasoning", val: entry.evaluation.reasoning_score },
                        ].map((s) => (
                          <div key={s.label}>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-white/40">{s.label}</span>
                              <span className={scoreColor(s.val, 5)}>{s.val}/5</span>
                            </div>
                            <div className="h-1.5 bg-surface-800 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full bg-gradient-to-r from-brand-500 to-brand-400"
                                style={{ width: `${(s.val / 5) * 100}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>

                      <p className="text-white/50 text-xs leading-relaxed">{entry.evaluation.feedback}</p>

                      {entry.evaluation.strengths.length > 0 && (
                        <div>
                          <span className="text-xs font-medium text-emerald-400">Strengths:</span>
                          <ul className="mt-1 space-y-0.5">
                            {entry.evaluation.strengths.map((s, j) => (
                              <li key={j} className="text-xs text-white/40 flex items-start gap-1">
                                <CheckCircle2 size={10} className="text-emerald-400 mt-0.5 shrink-0" />
                                {s}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {entry.evaluation.weaknesses.length > 0 && (
                        <div>
                          <span className="text-xs font-medium text-amber-400">Areas for improvement:</span>
                          <ul className="mt-1 space-y-0.5">
                            {entry.evaluation.weaknesses.map((w, j) => (
                              <li key={j} className="text-xs text-white/40 flex items-start gap-1">
                                <AlertCircle size={10} className="text-amber-400 mt-0.5 shrink-0" />
                                {w}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {/* ── Current Question ──────────────────────────────────── */}
          {currentQuestion && (
            <div className="animate-fade-in-up">
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center shrink-0 mt-0.5 animate-pulse-glow">
                  <Brain size={14} className="text-white" />
                </div>
                <div className="glass rounded-2xl rounded-tl-md p-4 max-w-[85%]">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${difficultyColor[currentQuestion.difficulty] || ""}`}
                    >
                      {currentQuestion.difficulty}
                    </span>
                    <span className="text-xs text-white/30">{currentQuestion.question_type}</span>
                    {currentQuestion.topic && (
                      <span className="text-xs text-white/20">• {currentQuestion.topic}</span>
                    )}
                    {currentQuestion.is_follow_up === 1 && (
                      <span className="text-xs text-brand-400">follow-up</span>
                    )}
                  </div>
                  <p className="text-sm leading-relaxed">{currentQuestion.question_text}</p>
                </div>
              </div>

              {/* Hint */}
              {hintText && (
                <div className="ml-11 mt-2 p-3 rounded-xl bg-amber-500/5 border border-amber-500/10 text-sm text-amber-300/80">
                  <Lightbulb size={14} className="inline mr-1.5" />
                  {hintText}
                  {hintsRemaining > 0 && (
                    <span className="text-xs text-white/30 ml-2">({hintsRemaining} hints left)</span>
                  )}
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
              {error}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </main>

      {/* ── Input Area ───────────────────────────────────────────── */}
      {currentQuestion && !completed && (
        <footer className="sticky bottom-0 glass border-t border-white/5">
          <div className="max-w-3xl mx-auto px-6 py-4">
            {/* Mode toggle */}
            <div className="flex items-center justify-end gap-2 mb-2">
              <button
                onClick={() => { setVoiceMode(false); resetRecording(); }}
                className={`flex items-center gap-1 px-3 py-1 rounded-lg text-xs transition-colors ${
                  !voiceMode ? "bg-brand-500/20 text-brand-300" : "text-white/30 hover:text-white/50"
                }`}
              >
                <Keyboard size={12} />
                Type
              </button>
              <button
                onClick={() => setVoiceMode(true)}
                className={`flex items-center gap-1 px-3 py-1 rounded-lg text-xs transition-colors ${
                  voiceMode ? "bg-cyan-500/20 text-cyan-300" : "text-white/30 hover:text-white/50"
                }`}
              >
                <Mic size={12} />
                Voice
              </button>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleGetHint}
                className="shrink-0 w-10 h-10 rounded-xl glass-light flex items-center justify-center text-amber-400 hover:bg-amber-500/10 transition-colors self-end"
                title="Get a hint"
              >
                <Lightbulb size={18} />
              </button>

              {!voiceMode ? (
                /* Text input */
                <div className="flex-1 relative">
                  <textarea
                    ref={answerRef}
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmitAnswer();
                      }
                    }}
                    placeholder="Type your answer here... (Enter to submit, Shift+Enter for new line)"
                    rows={3}
                    className="w-full px-4 py-3 pr-12 rounded-xl bg-surface-800 border border-white/5 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-brand-500/50 transition-colors resize-none"
                  />
                  <button
                    onClick={handleSubmitAnswer}
                    disabled={!answer.trim() || submitting}
                    className="absolute right-2 bottom-2 w-8 h-8 rounded-lg bg-gradient-to-r from-brand-500 to-brand-600 flex items-center justify-center text-white disabled:opacity-30 hover:opacity-90 transition-opacity"
                  >
                    {submitting ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                  </button>
                </div>
              ) : (
                /* Voice input */
                <div className="flex-1 flex items-center gap-3">
                  {!isRecording && !audioBlob ? (
                    <button
                      onClick={startRecording}
                      className="flex-1 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
                    >
                      <Mic size={18} />
                      Start Recording
                    </button>
                  ) : isRecording ? (
                    <>
                      <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20">
                        <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
                        <span className="text-sm text-red-300">Recording... {formatTime(recordingDuration)}</span>
                        <div className="flex-1 flex justify-center gap-0.5">
                          {[...Array(12)].map((_, i) => (
                            <div
                              key={i}
                              className="w-1 bg-red-400/50 rounded-full animate-pulse"
                              style={{
                                height: `${8 + Math.random() * 16}px`,
                                animationDelay: `${i * 0.08}s`,
                              }}
                            />
                          ))}
                        </div>
                      </div>
                      <button
                        onClick={stopRecording}
                        className="shrink-0 w-10 h-10 rounded-xl bg-red-500 flex items-center justify-center text-white hover:bg-red-600 transition-colors"
                      >
                        <MicOff size={18} />
                      </button>
                    </>
                  ) : audioBlob ? (
                    <>
                      <div className="flex-1 flex items-center gap-3 px-4 py-3 rounded-xl glass-light">
                        <AudioWaveform size={18} className="text-cyan-400" />
                        <span className="text-sm text-white/60">Recording ready ({formatTime(recordingDuration)})</span>
                      </div>
                      <button
                        onClick={resetRecording}
                        className="shrink-0 px-3 py-2 rounded-xl glass-light text-white/40 text-xs hover:text-white/70 transition-colors"
                      >
                        Redo
                      </button>
                      <button
                        onClick={handleSubmitVoiceAnswer}
                        disabled={submitting}
                        className="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-r from-brand-500 to-brand-600 flex items-center justify-center text-white disabled:opacity-30 hover:opacity-90 transition-opacity"
                      >
                        {submitting ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
                      </button>
                    </>
                  ) : null}
                </div>
              )}
            </div>
            {micError && (
              <p className="text-xs text-red-400 mt-2">{micError}</p>
            )}
          </div>
        </footer>
      )}
    </div>
  );
}
