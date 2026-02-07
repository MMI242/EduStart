import { api } from './client';

export interface AnalyticsEvent {
    id: string;
    child_id: string;
    module_id: string;
    is_correct: boolean;
    duration_ms: number;
    timestamp: string;
}

export interface AnalyticsEventCreate {
    module_id: string;
    question_id: string;
    question_type: string; // 'drag_drop', 'multiple_choice', etc.
    difficulty_level: number;
    is_correct: boolean;
    duration_ms: number;
    hesitation_ms: number;
    timestamp?: string;
}

export const analyticsApi = {
    trackEvent: async (childId: string, data: AnalyticsEventCreate): Promise<AnalyticsEvent> => {
        return api.post<AnalyticsEvent>(`/analytics/track/${childId}`, data);
    }
};
