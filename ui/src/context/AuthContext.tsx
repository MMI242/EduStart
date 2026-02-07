// Auth Context - State management for authentication
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { authApi } from '../api/auth';
import type { User } from '../api/auth';
import { tokenStorage } from '../api/client';

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    hasAcceptedPrivacyPolicy: boolean;
    login: (email: string, password: string) => Promise<User>;
    register: (email: string, password: string, role: 'parent' | 'educator', fullName?: string) => Promise<void>;
    logout: () => Promise<void>;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Check for existing session on mount
    useEffect(() => {
        const checkAuth = async () => {
            const token = tokenStorage.getAccessToken();
            if (token) {
                try {
                    const userData = await authApi.getMe();
                    setUser(userData);
                } catch {
                    // Token invalid, clear it
                    tokenStorage.clearTokens();
                }
            }
            setIsLoading(false);
        };
        checkAuth();
    }, []);

    const login = useCallback(async (email: string, password: string) => {
        await authApi.login({ email, password });
        const userData = await authApi.getMe();
        setUser(userData);
        return userData;
    }, []);

    const register = useCallback(async (
        email: string,
        password: string,
        role: 'parent' | 'educator',
        fullName?: string
    ) => {
        await authApi.register({ email, password, role, full_name: fullName });
        // Auto-login after registration
        await login(email, password);
    }, [login]);

    const logout = useCallback(async () => {
        await authApi.logout();
        setUser(null);
    }, []);

    const refreshUser = useCallback(async () => {
        try {
            const userData = await authApi.getMe();
            setUser(userData);
        } catch {
            // Token invalid, clear it
            tokenStorage.clearTokens();
            setUser(null);
        }
    }, []);

    const value: AuthContextType = {
        user,
        isLoading,
        isAuthenticated: !!user,
        hasAcceptedPrivacyPolicy: !!user?.privacy_policy_accepted_at,
        login,
        register,
        logout,
        refreshUser,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

// Protected Route wrapper
export function RequireAuth({ children, loginPath = '/login' }: { children: React.ReactNode; loginPath?: string }) {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center" style={{ minHeight: '100vh' }}>
                <div className="spinner" />
            </div>
        );
    }

    if (!isAuthenticated) {
        // Redirect to login with return url
        return <Navigate to={loginPath} replace state={{ from: window.location.pathname }} />;
    }

    return <>{children}</>;
}
