// Login Page
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/Button';
import './Auth.css';

export function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const user = await login(email, password);

            // Check if user has accepted privacy policy
            if (!user.privacy_policy_accepted_at) {
                navigate('/privacy-policy');
                return;
            }

            // Redirect to appropriate dashboard
            if (user.role === 'educator') {
                navigate('/teacher/dashboard');
            } else {
                navigate('/dashboard');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Login gagal. Silakan coba lagi.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-card">
                    <div className="auth-header">
                        <Link to="/" className="auth-logo">
                            <img src="/logo.png" alt="EduStart" className="logo-img" />
                            <span className="logo-text">EduStart</span>
                        </Link>
                        <h1>Selamat Datang! 👋</h1>
                        <p>Masuk untuk melanjutkan belajar</p>
                    </div>

                    <form onSubmit={handleSubmit} className="auth-form">
                        {error && (
                            <div className="auth-error">
                                <span>⚠️</span> {error}
                            </div>
                        )}

                        <div className="form-group">
                            <label htmlFor="email">Email</label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="nama@email.com"
                                required
                                autoComplete="email"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Kata Sandi</label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                autoComplete="current-password"
                            />
                        </div>

                        <Button
                            type="submit"
                            variant="primary"
                            size="lg"
                            fullWidth
                            isLoading={isLoading}
                        >
                            Masuk 🚀
                        </Button>
                    </form>

                    <div className="auth-footer">
                        <p>
                            Belum punya akun?{' '}
                            <Link to="/register">Daftar sekarang</Link>
                        </p>
                    </div>
                </div>

                <div className="auth-decoration">
                    <div className="deco-emoji deco-1">📚</div>
                    <div className="deco-emoji deco-2">✨</div>
                    <div className="deco-emoji deco-3">🌟</div>
                </div>
            </div>
        </div>
    );
}
