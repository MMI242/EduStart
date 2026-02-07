// Auth API functions
import { api, tokenStorage } from './client';

export interface User {
    id: string;
    email: string;
    role: 'parent' | 'educator';
    created_at: string;
    full_name?: string;
    privacy_policy_accepted_at?: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    role: 'parent' | 'educator';
    full_name?: string;
}

export const authApi = {
    login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
        const response = await api.post<TokenResponse>('/auth/login', credentials, {
            skipAuth: true,
        });
        tokenStorage.setTokens(response.access_token, response.refresh_token);
        return response;
    },

    register: async (data: RegisterData): Promise<User> => {
        return api.post<User>('/auth/register', data, { skipAuth: true });
    },

    logout: async (): Promise<void> => {
        try {
            await api.post('/auth/logout');
        } finally {
            tokenStorage.clearTokens();
        }
    },

    getMe: async (): Promise<User> => {
        return api.get<User>('/auth/me');
    },

    refreshToken: async (): Promise<TokenResponse> => {
        const refreshToken = tokenStorage.getRefreshToken();
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }
        const response = await api.post<TokenResponse>(
            `/auth/refresh?refresh_token=${refreshToken}`,
            undefined,
            { skipAuth: true }
        );
        tokenStorage.setTokens(response.access_token, response.refresh_token);
        return response;
    },

    acceptPrivacyPolicy: async (): Promise<void> => {
        await api.post('/auth/accept-privacy-policy');
    },
};
