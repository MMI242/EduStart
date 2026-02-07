// Children API functions
import { api } from './client';

export interface Child {
    id: string;
    name: string;
    age: number;
    avatar?: string;
    parent_id: string;
    current_level: number;
    total_points: number;
    created_at: string;
    updated_at: string;
}

export interface CreateChildData {
    name: string;
    age: number;
    avatar?: string;
}

export interface UpdateChildData {
    name?: string;
    age?: number;
    avatar?: string;
}

export const childrenApi = {
    getAll: async (): Promise<Child[]> => {
        return api.get<Child[]>('/children');
    },

    getById: async (id: string): Promise<Child> => {
        return api.get<Child>(`/children/${id}`);
    },

    create: async (data: CreateChildData): Promise<Child> => {
        return api.post<Child>('/children', data);
    },

    update: async (id: string, data: UpdateChildData): Promise<Child> => {
        return api.put<Child>(`/children/${id}`, data);
    },

    delete: async (id: string): Promise<void> => {
        return api.delete(`/children/${id}`);
    },
};
