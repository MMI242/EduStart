// Card Component - Kids-friendly content cards
import React from 'react';
import './Card.css';

interface CardProps {
    children: React.ReactNode;
    className?: string;
    variant?: 'default' | 'elevated' | 'colored';
    color?: 'purple' | 'orange' | 'teal' | 'pink';
    onClick?: () => void;
    hoverable?: boolean;
}

export function Card({
    children,
    className = '',
    variant = 'default',
    color,
    onClick,
    hoverable = false,
}: CardProps) {
    return (
        <div
            className={`card card-${variant} ${color ? `card-${color}` : ''} ${hoverable ? 'card-hoverable' : ''} ${className}`}
            onClick={onClick}
            role={onClick ? 'button' : undefined}
            tabIndex={onClick ? 0 : undefined}
        >
            {children}
        </div>
    );
}

// Card sub-components
export function CardHeader({ children, className = '' }: { children: React.ReactNode; className?: string }) {
    return <div className={`card-header ${className}`}>{children}</div>;
}

export function CardBody({ children, className = '' }: { children: React.ReactNode; className?: string }) {
    return <div className={`card-body ${className}`}>{children}</div>;
}

export function CardFooter({ children, className = '' }: { children: React.ReactNode; className?: string }) {
    return <div className={`card-footer ${className}`}>{children}</div>;
}
