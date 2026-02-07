// Dashboard Page
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/Button';
import { Card, CardBody } from '../components/Card';
import { childrenApi } from '../api/children';
import type { Child, CreateChildData } from '../api/children';
import { progressApi } from '../api/progress';
import type { ProgressSummary } from '../api/progress';
import './Dashboard.css';

export function Dashboard() {
    const { user, logout } = useAuth();
    const [children, setChildren] = useState<Child[]>([]);
    const [selectedChild, setSelectedChild] = useState<Child | null>(null);
    const [progressSummary, setProgressSummary] = useState<ProgressSummary | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Add Child Modal state
    const [showAddModal, setShowAddModal] = useState(false);
    const [newChildName, setNewChildName] = useState('');
    const [newChildAge, setNewChildAge] = useState(5);
    const [isAddingChild, setIsAddingChild] = useState(false);
    const [addError, setAddError] = useState('');

    // Safety check: Redirect educators to teacher dashboard
    useEffect(() => {
        if (user?.role === 'educator') {
            window.location.href = '/teacher/dashboard';
        }
    }, [user]);

    // Fetch children on mount
    useEffect(() => {
        fetchChildren();
    }, []);

    async function fetchChildren() {
        try {
            const data = await childrenApi.getAll();
            setChildren(data);
            if (data.length > 0 && !selectedChild) {
                setSelectedChild(data[0]);
            }
        } catch (error) {
            console.error('Failed to fetch children:', error);
        } finally {
            setIsLoading(false);
        }
    }

    // Fetch progress when child is selected
    useEffect(() => {
        if (!selectedChild) return;

        async function fetchProgress() {
            try {
                const summary = await progressApi.getSummary(selectedChild!.id);
                setProgressSummary(summary);
            } catch (error) {
                console.error('Failed to fetch progress:', error);
                setProgressSummary(null);
            }
        }
        fetchProgress();
    }, [selectedChild]);

    const handleLogout = async () => {
        await logout();
        window.location.href = '/';
    };

    const handleAddChild = async (e: React.FormEvent) => {
        e.preventDefault();
        setAddError('');

        if (!newChildName.trim()) {
            setAddError('Nama anak harus diisi');
            return;
        }

        if (newChildAge < 4 || newChildAge > 10) {
            setAddError('Usia harus antara 4-10 tahun');
            return;
        }

        setIsAddingChild(true);

        try {
            const childData: CreateChildData = {
                name: newChildName.trim(),
                age: newChildAge,
            };
            const newChild = await childrenApi.create(childData);
            setChildren([...children, newChild]);
            setSelectedChild(newChild);
            setShowAddModal(false);
            setNewChildName('');
            setNewChildAge(5);
        } catch (error) {
            console.error('Failed to add child:', error);
            setAddError('Gagal menambah anak. Silakan coba lagi.');
        } finally {
            setIsAddingChild(false);
        }
    };

    const handleStartLearning = (moduleType: string) => {
        // Navigate to module list with type filter and childId
        const typeMap: Record<string, string> = {
            'Membaca': 'reading',
            'Berhitung': 'counting',
            'Kognitif': 'cognitive',
        };
        const type = typeMap[moduleType] || '';
        const childParam = selectedChild ? `&childId=${selectedChild.id}` : '';
        window.location.href = `/modules?type=${type}${childParam}`;
    };

    if (isLoading) {
        return (
            <div className="dashboard-loading">
                <div className="spinner" />
                <p>Memuat...</p>
            </div>
        );
    }

    return (
        <div className="dashboard">
            {/* Header */}
            <header className="dashboard-header">
                <div className="container">
                    <div className="header-content">
                        <div className="logo">
                            <img src="/logo.png" alt="EduStart" className="logo-img" />
                            <span className="logo-text">EduStart</span>
                        </div>
                        <div className="header-right">
                            <span className="user-greeting">Halo, {user?.full_name || user?.email}!</span>
                            <Button variant="ghost" size="sm" onClick={handleLogout}>
                                Keluar
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="dashboard-main">
                <div className="container">
                    {/* Child Selector */}
                    {children.length > 0 ? (
                        <>
                            <section className="child-selector-section">
                                <h2>Pilih Profil Anak 👶</h2>
                                <div className="child-selector">
                                    {children.map((child) => (
                                        <button
                                            key={child.id}
                                            className={`child-avatar-btn ${selectedChild?.id === child.id ? 'active' : ''}`}
                                            onClick={() => setSelectedChild(child)}
                                        >
                                            <div className="child-avatar">
                                                {child.avatar || getAvatarEmoji(child.name)}
                                            </div>
                                            <span className="child-name">{child.name}</span>
                                            <span className="child-age">{child.age} tahun</span>
                                        </button>
                                    ))}
                                    <button
                                        className="add-child-btn"
                                        onClick={() => setShowAddModal(true)}
                                    >
                                        <span>➕</span>
                                        <span>Tambah</span>
                                    </button>
                                </div>
                            </section>

                            {selectedChild && (
                                <>
                                    {/* Stats Section */}
                                    <section className="stats-section">
                                        <h2>Progres {selectedChild.name} 📊</h2>
                                        <div className="stats-grid">
                                            <Card variant="colored" color="purple">
                                                <CardBody>
                                                    <div className="stat-card">
                                                        <span className="stat-icon">⭐</span>
                                                        <div className="stat-info">
                                                            <span className="stat-value">{selectedChild.total_points}</span>
                                                            <span className="stat-label">Total Poin</span>
                                                        </div>
                                                    </div>
                                                </CardBody>
                                            </Card>
                                            <Card variant="colored" color="orange">
                                                <CardBody>
                                                    <div className="stat-card">
                                                        <span className="stat-icon">🔥</span>
                                                        <div className="stat-info">
                                                            <span className="stat-value">{progressSummary?.current_streak_days || 0}</span>
                                                            <span className="stat-label">Hari Berturut</span>
                                                        </div>
                                                    </div>
                                                </CardBody>
                                            </Card>
                                            <Card variant="colored" color="teal">
                                                <CardBody>
                                                    <div className="stat-card">
                                                        <span className="stat-icon">📚</span>
                                                        <div className="stat-info">
                                                            <span className="stat-value">{progressSummary?.total_modules_completed || 0}</span>
                                                            <span className="stat-label">Modul Selesai</span>
                                                        </div>
                                                    </div>
                                                </CardBody>
                                            </Card>
                                            <Card variant="colored" color="pink">
                                                <CardBody>
                                                    <div className="stat-card">
                                                        <span className="stat-icon">🎯</span>
                                                        <div className="stat-info">
                                                            <span className="stat-value">{Math.round((progressSummary?.average_accuracy || 0) * 100)}%</span>
                                                            <span className="stat-label">Akurasi</span>
                                                        </div>
                                                    </div>
                                                </CardBody>
                                            </Card>
                                        </div>
                                    </section>

                                    {/* Quick Actions */}
                                    <section className="actions-section">
                                        <h2>Mulai Belajar 🚀</h2>
                                        <div className="actions-grid">
                                            <Card
                                                hoverable
                                                className="action-card action-reading"
                                                onClick={() => handleStartLearning('Membaca')}
                                            >
                                                <CardBody>
                                                    <span className="action-icon">📖</span>
                                                    <h3>Membaca</h3>
                                                    <p>Belajar huruf dan kata</p>
                                                </CardBody>
                                            </Card>
                                            <Card
                                                hoverable
                                                className="action-card action-counting"
                                                onClick={() => handleStartLearning('Berhitung')}
                                            >
                                                <CardBody>
                                                    <span className="action-icon">🔢</span>
                                                    <h3>Berhitung</h3>
                                                    <p>Latihan angka dan hitung</p>
                                                </CardBody>
                                            </Card>
                                            <Card
                                                hoverable
                                                className="action-card action-cognitive"
                                                onClick={() => handleStartLearning('Kognitif')}
                                            >
                                                <CardBody>
                                                    <span className="action-icon">🧩</span>
                                                    <h3>Kognitif</h3>
                                                    <p>Puzzle dan logika</p>
                                                </CardBody>
                                            </Card>
                                        </div>
                                    </section>

                                    {/* Level Info */}
                                    <section className="level-section">
                                        <Card>
                                            <CardBody>
                                                <div className="level-info">
                                                    <div className="level-badge">
                                                        <span>Level {selectedChild.current_level}</span>
                                                    </div>
                                                    <div className="level-progress">
                                                        <div
                                                            className="level-progress-bar"
                                                            style={{ width: `${(selectedChild.total_points % 100)}%` }}
                                                        />
                                                    </div>
                                                    <span className="level-text">
                                                        {100 - (selectedChild.total_points % 100)} poin lagi ke level berikutnya!
                                                    </span>
                                                </div>
                                            </CardBody>
                                        </Card>
                                    </section>
                                </>
                            )}
                        </>
                    ) : (
                        /* No children - show onboarding */
                        <section className="no-children">
                            <div className="no-children-content">
                                <span className="no-children-icon">👶</span>
                                <h2>Belum Ada Profil Anak</h2>
                                <p>Tambahkan profil anak untuk memulai petualangan belajar!</p>
                                <Button
                                    variant="primary"
                                    size="lg"
                                    onClick={() => setShowAddModal(true)}
                                >
                                    Tambah Anak Pertama ✨
                                </Button>
                            </div>
                        </section>
                    )}
                </div>
            </main>

            {/* Add Child Modal */}
            {showAddModal && (
                <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Tambah Profil Anak 👶</h2>
                            <button
                                className="modal-close"
                                onClick={() => setShowAddModal(false)}
                            >
                                ✕
                            </button>
                        </div>
                        <form onSubmit={handleAddChild} className="modal-body">
                            {addError && (
                                <div className="modal-error">
                                    ⚠️ {addError}
                                </div>
                            )}
                            <div className="form-group">
                                <label htmlFor="childName">Nama Anak</label>
                                <input
                                    id="childName"
                                    type="text"
                                    value={newChildName}
                                    onChange={(e) => setNewChildName(e.target.value)}
                                    placeholder="Masukkan nama anak"
                                    autoFocus
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="childAge">Usia (4-10 tahun)</label>
                                <input
                                    id="childAge"
                                    type="number"
                                    min={4}
                                    max={10}
                                    value={newChildAge}
                                    onChange={(e) => setNewChildAge(Number(e.target.value))}
                                />
                            </div>
                            <div className="modal-actions">
                                <Button
                                    type="button"
                                    variant="ghost"
                                    onClick={() => setShowAddModal(false)}
                                >
                                    Batal
                                </Button>
                                <Button
                                    type="submit"
                                    variant="primary"
                                    isLoading={isAddingChild}
                                >
                                    Tambah Anak
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

// Helper function to get avatar emoji from name
function getAvatarEmoji(name: string): string {
    const emojis = ['🦁', '🐯', '🐻', '🐼', '🐨', '🐸', '🦊', '🐰'];
    const index = name.charCodeAt(0) % emojis.length;
    return emojis[index];
}
