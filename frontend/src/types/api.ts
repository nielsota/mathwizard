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
  source: QuestionSource;
  topic: string;
  tags: string[];
  title: string;
  question_text: string;
  parts: QuestionPart[];
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

export type UserRole = 'teacher' | 'student';

export interface UserResponse {
  id: number;
  username: string;
  role: UserRole;
}

export interface StudentSummary {
  id: number;
  username: string;
}

export interface TeacherSummary {
  id: number;
  username: string;
}

export interface StudentsResponse {
  students: StudentSummary[];
}

export interface MyTeacherResponse {
  teacher: TeacherSummary;
}

export interface FunctionGraphElement {
  type: "functionGraph";
  fn: string;
  domain?: [number, number] | null;
  color?: string | null;
}

export type FigureElement = FunctionGraphElement;

export interface FigureViewport {
  x: [number, number];
  y?: [number, number] | null;
}

export interface FigureSpec {
  viewport: FigureViewport;
  show_grid: boolean;
  x_label: string;
  y_label: string;
  elements: FigureElement[];
}

export interface FigureSummary {
  id: number;
  slug: string;
  title: string;
  question_id?: number | null;
  part_id?: number | null;
}

export interface FigureResponse extends FigureSummary {
  description?: string | null;
  spec: FigureSpec;
}

export interface FigureListResponse {
  figures: FigureSummary[];
}
