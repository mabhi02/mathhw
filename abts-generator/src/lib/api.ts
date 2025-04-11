// File: abts-generator/src/lib/api.ts
import axios from "axios";

// Create an axios instance with base URL and default headers
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Types for API responses
export type QuestionOption = {
  id: string;
  question_id: string;
  text: string;
  is_correct: boolean;
  position: number;
  created_at: string;
  updated_at: string;
};

export type Question = {
  id: string;
  text: string;
  explanation: string;
  domain?: string;
  cognitive_complexity?: string;
  blooms_taxonomy_level?: string;
  surgically_appropriate?: boolean;
  question_type?: string;
  outline_id?: string;
  options: QuestionOption[];
  created_at: string;
  updated_at: string;
};

export type QuestionGenerationInput = {
  outline_id?: string;
  content?: string;
  question_type?: string;
  complexity?: string;
  count?: number;
};

export type QuestionGenerationResult = {
  questions: Question[];
  metadata: Record<string, any>;
  processing_time: number;
};

export type Template = {
  id: string;
  type: string;
  variables: string[];
  has_conditionals: boolean;
  description?: string;
  required_variables?: string[];
  optional_variables?: string[];
};

export type Outline = {
  id: string;
  title: string;
  description?: string;
  metadata?: Record<string, any>;
};

export type OutlineNode = {
  id: string;
  title: string;
  type: string;
  content?: string;
  children: OutlineNode[];
  metadata?: Record<string, any>;
  parent_id?: string;
};

export type ComparisonResult = {
  id: string;
  question_id: string;
  input_text: string;
  direct_output: string;
  agent_output: string;
  direct_processing_time_ms?: number;
  agent_processing_time_ms?: number;
  created_at: string;
  updated_at: string;
};

export type UserFeedback = {
  id: string;
  comparison_id: string;
  preferred_output: "direct" | "agent";
  rationale?: string;
  direct_rating?: number;
  agent_rating?: number;
  additional_notes?: string;
  created_at: string;
  updated_at: string;
};

// API methods

// Questions API
export const questionsApi = {
  getQuestions: async (params?: {
    domain?: string;
    complexity?: string;
    question_type?: string;
    outline_id?: string;
    keywords?: string[];
    skip?: number;
    limit?: number;
  }) => {
    const response = await api.get("/questions", { params });
    return response.data;
  },

  getQuestion: async (id: string) => {
    const response = await api.get(`/questions/${id}`);
    return response.data as Question;
  },

  createQuestion: async (question: any) => {
    const response = await api.post("/questions", question);
    return response.data as Question;
  },

  deleteQuestion: async (id: string) => {
    return api.delete(`/questions/${id}`);
  },

  generateQuestions: async (input: QuestionGenerationInput) => {
    const response = await api.post("/questions/generate", input);
    return response.data as QuestionGenerationResult;
  },
  
  generateQuestionsPreview: async (input: QuestionGenerationInput) => {
    const response = await api.post("/questions/generate/preview", input);
    return response.data as QuestionGenerationResult;
  },
};

// Templates API
export const templatesApi = {
  getTemplates: async () => {
    const response = await api.get("/templates");
    return response.data as Template[];
  },

  getTemplate: async (id: string) => {
    const response = await api.get(`/templates/${id}`);
    return response.data as Template;
  },

  renderTemplate: async (id: string, variables: Record<string, any>) => {
    const response = await api.post(`/templates/${id}/render`, { variables });
    return response.data;
  },

  validateTemplate: async (id: string, variables: Record<string, any>) => {
    const response = await api.post(`/templates/${id}/validate`, { variables });
    return response.data;
  },

  createTemplate: async (template: {
    template_id: string;
    template_type: string;
    template_text: string;
    metadata?: Record<string, any>;
  }) => {
    const response = await api.post("/templates", template);
    return response.data;
  },
};

// Outlines API
export const outlinesApi = {
  getOutlines: async () => {
    const response = await api.get("/outlines");
    return response.data as Outline[];
  },

  getOutline: async (id: string) => {
    const response = await api.get(`/outlines/${id}`);
    return response.data;
  },

  createOutline: async (data: {
    content: string;
    format: string;
    title?: string;
    metadata?: Record<string, any>;
  }) => {
    const response = await api.post("/outlines", data);
    return response.data;
  },

  uploadOutline: async (file: File, format: string, title?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("format", format);
    if (title) formData.append("title", title);

    const response = await api.post("/outlines/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  deleteOutline: async (id: string) => {
    return api.delete(`/outlines/${id}`);
  },

  validateOutline: async (id: string) => {
    const response = await api.post(`/outlines/${id}/validate`);
    return response.data;
  },
};

// Comparisons API
export const comparisonsApi = {
  getComparisons: async (questionId?: string) => {
    const response = await api.get("/comparisons", {
      params: { question_id: questionId },
    });
    return response.data as ComparisonResult[];
  },

  getComparison: async (id: string) => {
    const response = await api.get(`/comparisons/${id}`);
    return response.data;
  },

  createComparison: async (data: {
    question_id: string;
    input_text: string;
    direct_output: string;
    agent_output: string;
    direct_processing_time_ms?: number;
    agent_processing_time_ms?: number;
  }) => {
    const response = await api.post("/comparisons", data);
    return response.data;
  },

  deleteComparison: async (id: string) => {
    return api.delete(`/comparisons/${id}`);
  },
};

// Feedback API
export const feedbackApi = {
  getFeedback: async (id: string) => {
    const response = await api.get(`/feedback/${id}`);
    return response.data as UserFeedback;
  },

  getFeedbackByComparison: async (comparisonId: string) => {
    const response = await api.get(`/feedback/by-comparison/${comparisonId}`);
    return response.data as UserFeedback;
  },

  createFeedback: async (data: {
    comparison_id: string;
    preferred_output: "direct" | "agent";
    rationale?: string;
    direct_rating?: number;
    agent_rating?: number;
    additional_notes?: string;
  }) => {
    const response = await api.post("/feedback", data);
    return response.data as UserFeedback;
  },

  deleteFeedback: async (id: string) => {
    return api.delete(`/feedback/${id}`);
  },
};

export default api;