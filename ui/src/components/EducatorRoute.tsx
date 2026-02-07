// EducatorRoute.tsx - Protected route for educators only
import { Navigate, Outlet } from 'react-router-dom';
import React from 'react';
import { useAuth } from '../context/AuthContext';

interface RouteProps {
    children?: React.ReactNode;
}

export function EducatorRoute({ children }: RouteProps) {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return (
            <div className="loading-state">
                <div className="spinner" />
                <p>Verifying access...</p>
            </div>
        );
    }

    // Check if user is logged in
    if (!user) {
        return <Navigate to="/login" replace state={{ from: window.location }} />;
    }

    // Check if user has educator role
    if (user.role !== 'educator') {
        return <Navigate to="/dashboard" replace />;
    }

    return children ? <>{children}</> : <Outlet />;
}

export function ParentRoute({ children }: RouteProps) {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return (
            <div className="loading-state">
                <div className="spinner" />
            </div>
        );
    }

    if (!user || user.role !== 'parent') {
        return <Navigate to="/dashboard" replace />;
    }

    return children ? <>{children}</> : <Outlet />;
}
