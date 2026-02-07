// Progress & Recommendations API functions
import { api } from './client';
import type { Module } from './modules';

export interface ProgressSummary {
    child_id: string;
    total_time_minutes: number;
    total_modules_completed: number;
    total_questions_answered: number;
    average_accuracy: number;
    current_streak_days: number;
    total_points: number;
    favorite_module_type?: string;
    most_active_time?: string;
}

export interface ProgressEventCreate {
    module_id: string;
    question_id?: string;
    is_correct: boolean;
    time_taken_seconds: number;
    attempt_count?: number;
}

export interface ProgressResponse {
    id: string;
    child_id: string;
    module_id: string;
    question_id?: string;
    is_correct: boolean;
    time_taken_seconds: number;
    attempt_count: number;
    points_earned: number;
    created_at: string;
}

export interface RecommendedModule {
    module: Module;
    confidence_score: number;
    reasons: { factor: string; weight: number; description: string }[];
    expected_difficulty: number;
}

export interface RecommendationResponse {
    child_id: string;
    recommended_modules: RecommendedModule[];
    next_best_module: RecommendedModule;
    personalization_level: string;
    generated_at: string;
    valid_until: string;
}

export const progressApi = {
    getSummary: async (childId: string, days = 30): Promise<ProgressSummary> => {
        return api.get<ProgressSummary>(`/progress/children/${childId}/summary?days=${days}`);
    },

    saveProgress: async (childId: string, data: ProgressEventCreate): Promise<ProgressResponse> => {
        return api.post<ProgressResponse>(`/progress/children/${childId}/events`, data);
    },
};

export const recommendationsApi = {
    get: async (childId: string): Promise<RecommendationResponse> => {
        return api.get<RecommendationResponse>(`/recommendations/children/${childId}`);
    },

    getNextModule: async (childId: string): Promise<RecommendedModule> => {
        return api.get<RecommendedModule>(`/recommendations/children/${childId}/next-module`);
    },
};
