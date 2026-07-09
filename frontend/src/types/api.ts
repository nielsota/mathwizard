export interface QuestionPart {
  text: string;
}

export interface FormattedQuestion {
  stem: string;
  parts: QuestionPart[];
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

export interface PracticeExercise {
  number: number;
  exam_id: string;
  title: string;
  question_text: string;
  parts: string[];
  max_marks?: number;
  calculator_allowed: boolean;
  difficulty?: string;
  figure_images: string[];
}

export interface PracticeSet {
  title: string;
  subtitle: string;
  exercises: PracticeExercise[];
}
