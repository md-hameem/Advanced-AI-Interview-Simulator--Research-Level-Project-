import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

/* ─── Types ──────────────────────────────────────────────────────────── */

export interface Candidate {
  id: string;
  name: string;
  email: string | null;
  target_role: string | null;
  experience_years: number;
  skills: string[];
  created_at: string;
}

export interface Interview {
  id: string;
  candidate_id: string;
  interview_type: string;
  status: string;
  difficulty: string;
  persona: string;
  current_question_index: number;
  total_questions: number;
  started_at: string | null;
  completed_at: string | null;
  overall_score: number | null;
  technical_score: number | null;
  communication_score: number | null;
  problem_solving_score: number | null;
  recommendation: string | null;
  created_at: string;
}

export interface Question {
  id: string;
  order_index: number;
  question_text: string;
  question_type: string;
  difficulty: string;
  topic: string | null;
  is_follow_up: number;
  hints: string[];
  created_at: string;
}

export interface Evaluation {
  question_id: string;
  correctness_score: number;
  depth_score: number;
  clarity_score: number;
  reasoning_score: number;
  overall_question_score: number;
  feedback: string;
  strengths: string[];
  weaknesses: string[];
  next_question: Question | null;
  interview_completed: boolean;
}

export interface Report {
  interview_id: string;
  candidate_name: string;
  target_role: string | null;
  interview_type: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  problem_solving_score: number;
  recommendation: string;
  total_questions: number;
  questions_answered: number;
  strengths: string[];
  weaknesses: string[];
  detailed_feedback: string;
  study_recommendations?: string[];
  question_scores: {
    question: string;
    type: string;
    score: number;
    correctness: number;
    depth: number;
    clarity: number;
    reasoning: number;
  }[];
}

export interface AnalyticsOverview {
  total_candidates: number;
  total_interviews: number;
  completed_interviews: number;
  average_scores: {
    overall: number;
    technical: number;
    communication: number;
  };
}

/* ─── API Functions ──────────────────────────────────────────────────── */

// Candidates
export const createCandidate = (data: {
  name: string;
  email?: string;
  target_role?: string;
  experience_years?: number;
  skills?: string[];
}) => api.post<Candidate>("/candidates", data).then((r) => r.data);

export const getCandidates = () =>
  api.get<Candidate[]>("/candidates").then((r) => r.data);

export const getCandidate = (id: string) =>
  api.get<Candidate>(`/candidates/${id}`).then((r) => r.data);

// Interviews
export const createInterview = (data: {
  candidate_id: string;
  interview_type?: string;
  difficulty?: string;
  persona?: string;
  total_questions?: number;
}) => api.post<Interview>("/interviews", data).then((r) => r.data);

export const getInterviews = () =>
  api.get<Interview[]>("/interviews").then((r) => r.data);

export const getInterview = (id: string) =>
  api.get<Interview>(`/interviews/${id}`).then((r) => r.data);

export const generateSignedS3Url = async (key: string) => {
  const { data } = await api.post("/aws/sign-url", { key });
  return data;
};

export const getLearningPlan = async (candidateId: string) => {
  const { data } = await api.get(`/candidates/${candidateId}/learning-plan`);
  return data;
};
// Interview Flow
export const startInterview = (id: string) =>
  api.post<Question>(`/interviews/${id}/start`).then((r) => r.data);

export const submitAnswer = (interviewId: string, questionId: string, answer: string) =>
  api
    .post<Evaluation>(`/interviews/${interviewId}/questions/${questionId}/answer`, {
      answer_text: answer,
    })
    .then((r) => r.data);

export const getHint = (interviewId: string) =>
  api
    .post<{ hint: string; hints_remaining: number }>(`/interviews/${interviewId}/hint`)
    .then((r) => r.data);

export const getInterviewQuestions = (interviewId: string) =>
  api.get<Question[]>(`/interviews/${interviewId}/questions`).then((r) => r.data);

// Reports
export const getReport = (interviewId: string) =>
  api.get<Report>(`/interviews/${interviewId}/report`).then((r) => r.data);

// Analytics
export const getAnalyticsOverview = () =>
  api.get<AnalyticsOverview>("/analytics/overview").then((r) => r.data);

// Speech
export interface SpeechMetrics {
  transcript: string;
  words_per_minute: number;
  pause_count: number;
  average_pause_duration: number;
  filler_word_count: number;
  filler_words_detected: string[];
  filler_rate: number;
  word_count: number;
  confidence_score: number;
  total_duration_seconds: number;
  speaking_rate_variability: number;
  pitch_mean: number;
  pitch_std: number;
  energy_mean: number;
  energy_std: number;
}

export interface SpeechEvaluation extends Evaluation {
  speech_metrics: SpeechMetrics;
}

export const submitSpeechAnswer = async (
  interviewId: string,
  questionId: string,
  audioBlob: Blob
): Promise<SpeechEvaluation> => {
  const form = new FormData();
  form.append("audio", audioBlob, "recording.webm");
  const res = await axios.post<SpeechEvaluation>(
    `${API_BASE}/speech/answer/${interviewId}/${questionId}`,
    form,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return res.data;
};

export const analyzeSpeech = async (audioBlob: Blob): Promise<SpeechMetrics> => {
  const form = new FormData();
  form.append("audio", audioBlob, "recording.webm");
  const res = await axios.post<SpeechMetrics>(
    `${API_BASE}/speech/analyze`,
    form,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return res.data;
};

export default api;

// ─── Coding ───────────────────────────────────────────────────────────

export interface CodingQuestion {
  id: string;
  title: string;
  difficulty: string;
  description: string;
  starter_code: string;
  topics: string[];
  optimal_complexity: { time: string; space: string };
  num_test_cases: number;
}

export interface TestResult {
  test_index: number;
  passed: boolean;
  input: Record<string, unknown>;
  expected: unknown;
  actual: unknown;
  error?: string;
  execution_time_ms: number;
}

export interface TestResults {
  total_tests: number;
  passed: number;
  failed: number;
  pass_rate: number;
  results: TestResult[];
}

export interface CodeReview {
  code_quality_score: number;
  correctness_score: number;
  efficiency_score: number;
  style_score: number;
  overall_code_score: number;
  feedback: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  edge_cases_missed: string[];
  optimal_approach: string;
}

export interface CodeEvaluationResult {
  question_id: string;
  question_title: string;
  language: string;
  test_results: TestResults;
  complexity: { time: string; space: string; details: Record<string, unknown> };
  review: CodeReview;
  optimal_complexity: { time: string; space: string };
}

export interface ExecutionResult {
  success: boolean;
  stdout: string;
  stderr: string;
  error?: string;
  execution_time_ms: number;
}

export const getCodingQuestions = (difficulty?: string) =>
  api.get<{ id: string; title: string; difficulty: string; topics: string[] }[]>(
    "/coding/questions",
    { params: difficulty ? { difficulty } : {} }
  ).then((r) => r.data);

export const getCodingQuestion = (id: string, language: string = "python") =>
  api.get<CodingQuestion>(`/coding/questions/${id}`, { params: { language } }).then((r) => r.data);

export const getRandomCodingQuestion = (difficulty: string = "easy", language: string = "python") =>
  api.get<CodingQuestion>("/coding/random", { params: { difficulty, language } }).then((r) => r.data);

export const executeCode = (code: string, language: string = "python", stdin: string = "") =>
  api.post<ExecutionResult>("/coding/execute", { code, language, stdin }).then((r) => r.data);

export const runCodeTests = (questionId: string, code: string, language: string = "python") =>
  api.post<TestResults>(`/coding/test/${questionId}`, { code, language }).then((r) => r.data);

export const evaluateCode = (questionId: string, code: string, language: string = "python") =>
  api.post<CodeEvaluationResult>(`/coding/evaluate/${questionId}`, { code, language }).then((r) => r.data);

export const analyzeComplexity = (code: string, language: string = "python") =>
  api.post<{ time: string; space: string; details: Record<string, unknown> }>("/coding/complexity", { code, language }).then((r) => r.data);

// ─── Behavioral ──────────────────────────────────────────────────────

export interface BehavioralQuestion {
  id: string;
  question: string;
  competency: string;
  difficulty: string;
  follow_ups: string[];
}

export interface StarComponent {
  detected: boolean;
  confidence: string;
  score: number;
  matched_indicators: string[];
  indicator_count: number;
}

export interface StarDetection {
  components: Record<string, StarComponent>;
  overall_star_score: number;
  components_present: number;
  components_total: number;
  star_completeness: string;
  is_complete_star: boolean;
}

export interface BehavioralAnalysis {
  situation_score: number;
  situation_summary: string;
  task_score: number;
  task_summary: string;
  action_score: number;
  action_summary: string;
  result_score: number;
  result_summary: string;
  competency_score: number;
  communication_score: number;
  specificity_score: number;
  impact_score: number;
  overall_behavioral_score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
  missing_elements: string[];
  red_flags: string[];
}

export interface BehavioralResult {
  question_id: string;
  question_text: string;
  competency: string;
  star_detection: StarDetection;
  analysis: BehavioralAnalysis;
  follow_up_questions: string[];
}

export const getBehavioralCompetencies = () =>
  api.get<{ competencies: string[] }>("/behavioral/competencies").then((r) => r.data.competencies);

export const getBehavioralQuestions = (competency?: string) =>
  api.get<{ id: string; question: string; competency: string; difficulty: string }[]>(
    "/behavioral/questions",
    { params: competency ? { competency } : {} }
  ).then((r) => r.data);

export const getBehavioralQuestion = (id: string) =>
  api.get<BehavioralQuestion>(`/behavioral/questions/${id}`).then((r) => r.data);

export const detectStar = (answer: string) =>
  api.post<StarDetection>("/behavioral/detect-star", { answer }).then((r) => r.data);

export const analyzeBehavioral = (questionId: string, answer: string) =>
  api.post<BehavioralResult>(`/behavioral/analyze/${questionId}`, { answer }).then((r) => r.data);
