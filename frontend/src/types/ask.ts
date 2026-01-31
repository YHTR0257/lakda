export interface Question {
  id: string;
  text: string;
  timestamp: string;
}

export interface Interpretation {
  id: string;
  questionId: string;
  originalQuestion: string;
  interpretedQuery: string;
  keywords: string[];
  intent: string;
  timestamp: string;
  confidenceScore: number;
}

export interface Answer {
  id: string;
  interpretationId: string;
  answerText: string;
  sources: Source[];
  timestamp: string;
  confidenceScore: number;
}

export interface Source {
  documentId: string;
  title: string;
  excerpt: string;
  relevanceScore: number;
}

export interface AskState {
  questionId: string;
  interpretationId: string;
  answerId: string;
  loading: boolean;
  error: string | null;
}

export interface ApiError {
  error: string;
  code?: string;
  details?: Record<string, any>;
}
