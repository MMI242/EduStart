// Register Page
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/Button';
import './Auth.css';

export function Register() {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        fullName: '',
        role: 'parent' as 'parent' | 'educator',
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Kata sandi tidak cocok');
            return;
        }

        if (formData.password.length < 8) {
            setError('Kata sandi minimal 8 karakter');
            return;
        }

        setIsLoading(true);

        try {
            await register(
                formData.email,
                formData.password,
                formData.role,
                formData.fullName || undefined
            );
            navigate('/dashboard');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Pendaftaran gagal. Silakan coba lagi.');
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
                        <h1>Bergabung Sekarang! 🎉</h1>
                        <p>Daftarkan diri untuk memulai</p>
                    </div>

                    <form onSubmit={handleSubmit} className="auth-form">
                        {error && (
                            <div className="auth-error">
                                <span>⚠️</span> {error}
                            </div>
                        )}

                        <div className="form-group">
                            <label htmlFor="fullName">Nama Lengkap</label>
                            <input
                                id="fullName"
                                name="fullName"
                                type="text"
                                value={formData.fullName}
                                onChange={handleChange}
                                placeholder="Nama lengkap Anda"
                                autoComplete="name"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="email">Email *</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="nama@email.com"
                                required
                                autoComplete="email"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="role">Saya adalah *</label>
                            <select
                                id="role"
                                name="role"
                                value={formData.role}
                                onChange={handleChange}
                                required
                            >
                                <option value="parent">👨‍👩‍👧 Orang Tua</option>
                                <option value="educator">👩‍🏫 Pendidik</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Kata Sandi *</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Minimal 8 karakter"
                                required
                                autoComplete="new-password"
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="confirmPassword">Konfirmasi Kata Sandi *</label>
                            <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="Ulangi kata sandi"
                                required
                                autoComplete="new-password"
                            />
                        </div>

                        <Button
                            type="submit"
                            variant="primary"
                            size="lg"
                            fullWidth
                            isLoading={isLoading}
                        >
                            Daftar Sekarang 🚀
                        </Button>
                    </form>

                    <div className="auth-footer">
                        <p>
                            Sudah punya akun?{' '}
                            <Link to="/login">Masuk di sini</Link>
                        </p>
                    </div>
                </div>

                <div className="auth-decoration">
                    <div className="deco-emoji deco-1">🎨</div>
                    <div className="deco-emoji deco-2">🌈</div>
                    <div className="deco-emoji deco-3">🎯</div>
                </div>
            </div>
        </div>
    );
}
