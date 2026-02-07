// Select Profile Page - Choose which child is learning
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { childrenApi } from '../api/children';
import type { Child } from '../api/children';
import { Button } from '../components/Button';
import './Auth.css'; // Reuse auth styles for consistency

export function SelectProfile() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const [children, setChildren] = useState<Child[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        async function fetchChildren() {
            try {
                const data = await childrenApi.getAll();
                setChildren(data);

                // If no children, redirect to dashboard to add one (or show empty state)
                // For now, let's keep it simple: if empty, maybe redirecting to dashboard is best
                // so parent can add a child.
                if (data.length === 0) {
                    // navigate('/dashboard'); // Optional: auto-redirect
                }
            } catch (error) {
                console.error('Failed to fetch children:', error);
            } finally {
                setIsLoading(false);
            }
        }
        fetchChildren();
    }, [navigate]);

    const handleSelectChild = (childId: string) => {
        navigate(`/modules?childId=${childId}`);
    };

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    // Helper to get avatar emoji
    const getAvatarEmoji = (name: string): string => {
        const emojis = ['🦁', '🐯', '🐻', '🐼', '🐨', '🐸', '🦊', '🐰'];
        const index = name.charCodeAt(0) % emojis.length;
        return emojis[index];
    };

    if (isLoading) {
        return (
            <div className="auth-page">
                <div className="auth-container">
                    <div className="loading-state" style={{ color: 'white', textAlign: 'center' }}>
                        <div className="spinner" />
                        <p>Memuat profil...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-page">
            <div className="auth-container" style={{ maxWidth: '800px' }}>
                <div className="auth-card">
                    <div className="auth-header">
                        <h1>Siapa yang mau belajar? 👶</h1>
                        <p>Pilih profilmu untuk memulai!</p>
                    </div>

                    {children.length > 0 ? (
                        <div className="profile-grid" style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                            gap: '2rem',
                            margin: '2rem 0'
                        }}>
                            {children.map((child) => (
                                <button
                                    key={child.id}
                                    onClick={() => handleSelectChild(child.id)}
                                    className="profile-card"
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: '1rem',
                                        transition: 'transform 0.2s ease'
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                    onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                >
                                    <div className="avatar-circle" style={{
                                        width: '120px',
                                        height: '120px',
                                        borderRadius: '50%',
                                        background: 'var(--primary-gradient)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '4rem',
                                        boxShadow: 'var(--shadow-md)',
                                        border: '4px solid white'
                                    }}>
                                        {child.avatar || getAvatarEmoji(child.name)}
                                    </div>
                                    <span style={{
                                        fontSize: '1.25rem',
                                        fontWeight: '700',
                                        color: 'var(--gray-800)'
                                    }}>
                                        {child.name}
                                    </span>
                                </button>
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state" style={{ textAlign: 'center', padding: '2rem 0' }}>
                            <span style={{ fontSize: '3rem', display: 'block', marginBottom: '1rem' }}>👶</span>
                            <h3>Belum ada profil anak</h3>
                            <p style={{ marginBottom: '1.5rem', color: 'var(--gray-600)' }}>
                                Minta orang tua untuk membuat profil terlebih dahulu di Dashboard.
                            </p>
                            <Button
                                variant="primary"
                                onClick={() => navigate('/dashboard')}
                            >
                                Pergi ke Dashboard Orang Tua
                            </Button>
                        </div>
                    )}

                    <div className="auth-footer">
                        <Button
                            variant="ghost"
                            onClick={handleLogout}
                            style={{ color: 'var(--gray-500)' }}
                        >
                            ← Bukan akunmu? Keluar
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
