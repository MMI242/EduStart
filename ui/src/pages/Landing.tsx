// Landing Page - Kids-friendly hero with features
import { Link } from 'react-router-dom';
import { Button } from '../components/Button';
import './Landing.css';

export function Landing() {
    return (
        <div className="landing">
            {/* Navigation */}
            <nav className="landing-nav">
                <div className="container">
                    <div className="nav-content">
                        <div className="logo">
                            <img src="/logo.png" alt="EduStart" className="logo-img" />
                            <span className="logo-text">EduStart</span>
                        </div>
                        <div className="nav-actions">
                            <Link to="/login">
                                <Button variant="ghost">Masuk</Button>
                            </Link>
                            <Link to="/register">
                                <Button variant="primary">Mulai Sekarang</Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="hero">
                <div className="container">
                    <div className="hero-content">
                        <div className="hero-text">
                            <h1 className="hero-title">
                                Belajar Jadi Lebih
                                <span className="text-gradient"> Menyenangkan! </span>
                                🎉
                            </h1>
                            <p className="hero-subtitle">
                                Platform pembelajaran interaktif untuk anak usia 4-10 tahun.
                                Membaca, berhitung, dan kognitif dengan cara yang seru!
                            </p>
                            <div className="hero-actions">
                                <Link to="/register">
                                    <Button variant="primary" size="lg">
                                        Mulai Belajar 🚀
                                    </Button>
                                </Link>
                                <Link to="/login-student">
                                    <Button variant="secondary" size="lg">
                                        Masuk Siswa 🎓
                                    </Button>
                                </Link>
                                <Link to="/login">
                                    <Button variant="outline" size="lg">
                                        Sudah Punya Akun
                                    </Button>
                                </Link>
                            </div>
                        </div>
                        <div className="hero-visual">
                            <div className="hero-illustration">
                                <img src="/logo.png" alt="EduStart" className="hero-logo" />
                                <div className="floating-emoji emoji-1">📚</div>
                                <div className="floating-emoji emoji-2">🔢</div>
                                <div className="floating-emoji emoji-3">🧩</div>
                                <div className="floating-emoji emoji-4">⭐</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features">
                <div className="container">
                    <h2 className="features-title">Apa yang Bisa Dipelajari?</h2>
                    <div className="features-grid">
                        <div className="feature-card feature-reading">
                            <div className="feature-icon">📖</div>
                            <h3>Membaca</h3>
                            <p>Belajar mengenal huruf, kata, dan kalimat dengan cerita interaktif yang menarik</p>
                        </div>
                        <div className="feature-card feature-counting">
                            <div className="feature-icon">🔢</div>
                            <h3>Berhitung</h3>
                            <p>Matematika dasar jadi mudah dengan game angka dan latihan seru</p>
                        </div>
                        <div className="feature-card feature-cognitive">
                            <div className="feature-icon">🧠</div>
                            <h3>Kognitif</h3>
                            <p>Asah logika dan kreativitas dengan puzzle dan tantangan menarik</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Benefits Section */}
            <section className="benefits">
                <div className="container">
                    <div className="benefits-content">
                        <div className="benefit-item">
                            <span className="benefit-icon">🎯</span>
                            <div>
                                <h4>Pembelajaran Adaptif</h4>
                                <p>AI yang menyesuaikan tingkat kesulitan dengan kemampuan anak</p>
                            </div>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">📊</span>
                            <div>
                                <h4>Laporan Progress</h4>
                                <p>Pantau perkembangan anak dengan laporan detail</p>
                            </div>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">🏆</span>
                            <div>
                                <h4>Gamifikasi</h4>
                                <p>Poin, badge, dan reward untuk motivasi belajar</p>
                            </div>
                        </div>
                        <div className="benefit-item">
                            <span className="benefit-icon">📱</span>
                            <div>
                                <h4>Mode Offline</h4>
                                <p>Belajar kapan saja, di mana saja tanpa internet</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta">
                <div className="container">
                    <div className="cta-content">
                        <h2>Siap Memulai Petualangan Belajar?</h2>
                        <p>Daftarkan anak Anda di EduStart sekarang dan lihat mereka tumbuh!</p>
                        <Link to="/register">
                            <Button variant="secondary" size="lg">
                                Daftar Gratis
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="landing-footer">
                <div className="container">
                    <div className="footer-content">
                        <div className="logo">
                            <img src="/logo.png" alt="EduStart" className="logo-img" />
                            <span className="logo-text">EduStart</span>
                        </div>
                        <p>© 2025 EduStart. Dibuat dengan ❤️ untuk pembelajaran.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
