export interface FormattedQuestion {
  stem: string;
  parts: SearchQuestionPart[];
}

export interface FetchResponse {
  record_id: string;
  exam_id: string;
  question_number: number;
  score: number;
  page_images: string[];
  figure_images: string[];
  formatted: FormattedQuestion;
}

export interface FetchRequest {
  query: string;
  mode: "best" | "random";
  max_results: number;
}

export interface SearchQuestionPart {
  text: string;
}

export type QuestionSource = 'practice' | 'exam' | 'generated';

export interface QuestionPart {
  label: string;
  text: string;
  points: number;
}

export interface QuestionResponse {
  id: number;
  number: number;
  source: QuestionSource;
  topic: string;
  tags: string[];
  title: string;
  question_text: string;
  parts: string[];
  part_details: QuestionPart[];
  max_marks: number;
  calculator_allowed?: boolean | null;
  difficulty?: number | null;
  figure_images: string[];
}

export interface QuestionListResponse {
  source: QuestionSource;
  topic?: string | null;
  questions: QuestionResponse[];
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface UserResponse {
  id: number;
  username: string;
}
