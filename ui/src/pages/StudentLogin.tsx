// Student Login Page
import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/Button';
import './Auth.css'; // Reuse auth styles

export function StudentLogin() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    // Get the return url from location state (set by RequireAuth)
    const from = location.state?.from?.pathname || '/select-profile';

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await login(email, password);
            navigate(from, { replace: true });
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
                        <h1>Masuk untuk Belajar 🚀</h1>
                        <p>Ayo mulai petualangan belajarmu!</p>
                    </div>

                    <form onSubmit={handleSubmit} className="auth-form">
                        {error && (
                            <div className="auth-error">
                                <span>⚠️</span> {error}
                            </div>
                        )}

                        <div className="form-group">
                            <label htmlFor="email">Email Orang Tua</label>
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
                            Mulai Bermain! ⭐
                        </Button>
                    </form>

                    <div className="auth-footer">
                        <p>
                            Pengajar?{' '}
                            <Link to="/login">Masuk di sini</Link>
                        </p>
                    </div>
                </div>

                <div className="auth-decoration">
                    <div className="deco-emoji deco-1">🦁</div>
                    <div className="deco-emoji deco-2">🎈</div>
                    <div className="deco-emoji deco-3">🎨</div>
                </div>
            </div>
        </div>
    );
}
