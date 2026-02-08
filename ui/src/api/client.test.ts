import { describe, it, expect, vi, beforeEach } from 'vitest';
import { tokenStorage, ApiError } from './client';

describe('tokenStorage', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it('should set and get access token', () => {
        tokenStorage.setTokens('access-123', 'refresh-456');
        expect(tokenStorage.getAccessToken()).toBe('access-123');
    });

    it('should set and get refresh token', () => {
        tokenStorage.setTokens('access-123', 'refresh-456');
        expect(tokenStorage.getRefreshToken()).toBe('refresh-456');
    });

    it('should clear tokens', () => {
        tokenStorage.setTokens('access-123', 'refresh-456');
        tokenStorage.clearTokens();
        expect(tokenStorage.getAccessToken()).toBeNull();
        expect(tokenStorage.getRefreshToken()).toBeNull();
    });
});

describe('ApiError', () => {
    it('should create an error with status and data', () => {
        const data = { detail: 'Not Found' };
        const error = new ApiError('Error message', 404, data);

        expect(error.message).toBe('Error message');
        expect(error.status).toBe(404);
        expect(error.data).toEqual(data);
        expect(error.name).toBe('ApiError');
    });
});
