// Modules API functions
import { api } from './client';

export interface Module {
    id: string;
    title: string;
    description: string;
    type: 'reading' | 'counting' | 'cognitive';  // Backend uses 'type'
    education_level: 'TK' | 'SD1' | 'SD2' | 'SD3' | 'SD4' | 'SD5' | 'SD6' | 'SMP' | 'SMA';
    difficulty_level: number;
    estimated_duration_minutes: number;
    thumbnail_url?: string;
    total_questions: number;
    points_reward: number;
}

// Alias for frontend compatibility
export interface ModuleWithType extends Module {
    module_type: 'reading' | 'counting' | 'cognitive';
}

export interface ModuleDetail extends Module {
    questions: Question[];
    learning_objectives?: string[];
    created_at?: string;
    updated_at?: string;
}

export interface Question {
    id: string;
    question_text: string;
    question_type: string;
    options?: string[];
    correct_answer: string;
    media_url?: string;
    audio_url?: string;
    hints?: string[];
    matching_pairs?: { left: string, right: string }[];
    points?: number;
}

export interface ModuleFilters {
    module_type?: string;
    difficulty_level?: number;
    skip?: number;
    limit?: number;
}

// Transform backend response to include module_type for frontend
function transformModule(module: Module): ModuleWithType {
    return {
        ...module,
        module_type: module.type,
    };
}

export const modulesApi = {
    getAll: async (filters?: ModuleFilters): Promise<ModuleWithType[]> => {
        const params = new URLSearchParams();
        if (filters?.module_type) params.append('module_type', filters.module_type);
        if (filters?.difficulty_level) params.append('difficulty_level', filters.difficulty_level.toString());
        if (filters?.skip) params.append('skip', filters.skip.toString());
        if (filters?.limit) params.append('limit', filters.limit.toString());

        const query = params.toString();
        const modules = await api.get<Module[]>(`/modules${query ? `?${query}` : ''}`);
        return modules.map(transformModule);
    },

    getById: async (id: string): Promise<ModuleDetail & { module_type: string }> => {
        const module = await api.get<ModuleDetail>(`/modules/${id}`);
        return {
            ...module,
            module_type: module.type,
        };
    },

    getTypes: async (): Promise<{ types: string[] }> => {
        return api.get<{ types: string[] }>('/modules/types/list');
    },

    create: async (data: ModuleCreate): Promise<ModuleWithType> => {
        const module = await api.post<Module>('/modules', data);
        return transformModule(module);
    },

    update: async (id: string, data: ModuleUpdate): Promise<ModuleWithType> => {
        const module = await api.put<Module>(`/modules/${id}`, data);
        return transformModule(module);
    },

    delete: async (id: string): Promise<boolean> => {
        return api.delete<boolean>(`/modules/${id}`);
    }
};

export interface ModuleCreate {
    title: string;
    description: string;
    module_type: string;
    education_level: string;
    difficulty_level: number;
    estimated_duration_minutes: number;
    thumbnail_url?: string;
    is_premium?: boolean;
    content: {
        questions: Question[];
        learning_objectives?: string[];
    };
}

export interface ModuleUpdate extends Partial<ModuleCreate> { }
