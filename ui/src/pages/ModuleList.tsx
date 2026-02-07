// Module List Page - Browse available learning modules
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/Button';
import { Card, CardBody } from '../components/Card';
import { modulesApi } from '../api/modules';
import type { Module } from '../api/modules';
import { childrenApi } from '../api/children';
import type { Child } from '../api/children';
import './ModuleList.css';

export function ModuleList() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const typeFilter = searchParams.get('type') || '';
    const childId = searchParams.get('childId');
    const { user, logout } = useAuth();

    const [child, setChild] = useState<Child | null>(null);

    const [modules, setModules] = useState<Module[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedType, setSelectedType] = useState(typeFilter);

    useEffect(() => {
        async function fetchModules() {
            setIsLoading(true);
            try {
                const data = await modulesApi.getAll(
                    selectedType ? { module_type: selectedType } : undefined
                );
                setModules(data);
            } catch (error) {
                console.error('Failed to fetch modules:', error);
            } finally {
                setIsLoading(false);
            }
        }
        fetchModules();
    }, [selectedType]);

    // Fetch child details if childId is present
    useEffect(() => {
        async function fetchChild() {
            if (!childId) return;
            try {
                const data = await childrenApi.getById(childId);
                setChild(data);
            } catch (error) {
                console.error('Failed to fetch child details:', error);
            }
        }
        fetchChild();
    }, [childId]);

    const getModuleIcon = (type: string) => {
        switch (type) {
            case 'reading': return '📖';
            case 'counting': return '🔢';
            case 'cognitive': return '🧩';
            default: return '📚';
        }
    };

    const getModuleColor = (type: string) => {
        switch (type) {
            case 'reading': return 'reading';
            case 'counting': return 'counting';
            case 'cognitive': return 'cognitive';
            default: return '';
        }
    };

    const getDifficultyLabel = (level: number) => {
        if (level <= 3) return { text: 'Mudah', color: 'easy' };
        if (level <= 6) return { text: 'Sedang', color: 'medium' };
        return { text: 'Sulit', color: 'hard' };
    };

    const typeLabels: Record<string, string> = {
        '': 'Semua',
        'reading': 'Membaca',
        'counting': 'Berhitung',
        'cognitive': 'Kognitif',
    };

    return (
        <div className="module-list-page">
            {/* Header */}
            <header className="module-list-header">
                <div className="container">
                    <div className="header-content">
                        <div className="header-left">
                            <h1>Pilih Modul Belajar 📚</h1>
                        </div>
                        <div className="header-right" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <span className="user-greeting" style={{ fontWeight: 600, color: 'var(--gray-700)' }}>
                                Halo, {child ? child.name : (user?.full_name || user?.email)}! {child && '👋'}
                            </span>
                            <Button variant="ghost" size="sm" onClick={() => { logout(); navigate('/'); }}>
                                Keluar
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="module-list-main">
                <div className="container">
                    {/* Type Filter */}
                    <div className="type-filter">
                        {Object.entries(typeLabels).map(([type, label]) => (
                            <button
                                key={type}
                                className={`filter-btn ${selectedType === type ? 'active' : ''}`}
                                onClick={() => setSelectedType(type)}
                            >
                                {type && getModuleIcon(type)} {label}
                            </button>
                        ))}
                    </div>

                    {/* Module Grid */}
                    {isLoading ? (
                        <div className="loading-state">
                            <div className="spinner" />
                            <p>Memuat modul...</p>
                        </div>
                    ) : modules.length === 0 ? (
                        <div className="empty-state">
                            <span className="empty-icon">📭</span>
                            <h2>Belum ada modul tersedia</h2>
                            <p>Modul pembelajaran akan segera hadir!</p>
                        </div>
                    ) : (
                        <div className="modules-grid">
                            {modules.map((module) => {
                                const difficulty = getDifficultyLabel(module.difficulty_level);
                                return (
                                    <Card
                                        key={module.id}
                                        hoverable
                                        className={`module-card module-${getModuleColor(module.type)}`}
                                        onClick={() => navigate(`/learn/${module.id}${childId ? `?childId=${childId}` : ''}`)}
                                    >
                                        <CardBody>
                                            <div className="module-icon">
                                                {getModuleIcon(module.type)}
                                            </div>
                                            <h3>{module.title}</h3>
                                            <p className="module-description">{module.description}</p>
                                            <div className="module-meta">
                                                <span className={`difficulty ${difficulty.color}`}>
                                                    {difficulty.text}
                                                </span>
                                                <span className="duration">
                                                    ⏱️ {module.estimated_duration_minutes} menit
                                                </span>
                                            </div>
                                        </CardBody>
                                    </Card>
                                );
                            })}
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
