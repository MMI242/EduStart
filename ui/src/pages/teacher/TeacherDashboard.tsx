// Teacher Dashboard Page
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/Button';
import { useAuth } from '../../context/AuthContext';
import { modulesApi } from '../../api/modules';
import type { ModuleWithType } from '../../api/modules';
import './TeacherDashboard.css';

export function TeacherDashboard() {
    const navigate = useNavigate();
    const { logout } = useAuth();
    const [modules, setModules] = useState<ModuleWithType[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadModules();
    }, []);

    const loadModules = async () => {
        try {
            const data = await modulesApi.getAll();
            setModules(data);
        } catch (error) {
            console.error('Failed to load modules:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (_moduleId: string) => {
        if (!confirm('Apakah anda yakin ingin menghapus modul ini?')) return;

        try {
            // TODO: Implement delete API in frontend
            // await modulesApi.delete(moduleId);
            alert('Fitur hapus belum diimplementasikan di frontend API');
        } catch (error) {
            console.error('Failed to delete module:', error);
        }
    };

    const totalStudents = 125; // Dummy data
    const activeModules = modules.length;
    const completionRate = "85%"; // Dummy data

    return (
        <div className="teacher-dashboard">
            <header className="teacher-header">
                <div className="container">
                    <div className="header-content">
                        <div className="logo">
                            <img src="/logo.png" alt="EduStart" className="logo-img" />
                            <span className="logo-text">EduStart</span>
                            <span className="badge badge-reading" style={{ marginLeft: '1rem' }}>Pengajar</span>
                        </div>
                        <div className="teacher-nav">
                            <Button variant="outline" size="sm" onClick={() => navigate('/dashboard')}>
                                Lihat Mode Siswa
                            </Button>
                            <Button variant="ghost" size="sm" onClick={() => { logout(); navigate('/'); }}>
                                Keluar
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="dashboard-content">
                <div className="stats-overview">
                    <div className="stat-card">
                        <span className="stat-label">Total Siswa Aktif</span>
                        <span className="stat-value">{totalStudents}</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-label">Modul Aktif</span>
                        <span className="stat-value">{activeModules}</span>
                    </div>
                    <div className="stat-card">
                        <span className="stat-label">Tingkat Penyelesaian</span>
                        <span className="stat-value">{completionRate}</span>
                    </div>
                </div>

                <div className="modules-section">
                    <div className="section-header">
                        <h2>Daftar Modul Pembelajaran</h2>
                        <Button variant="primary" onClick={() => navigate('/teacher/modules/new')}>
                            + Buat Modul Baru
                        </Button>
                    </div>

                    {isLoading ? (
                        <p>Memuat modul...</p>
                    ) : (
                        <table className="modules-table">
                            <thead>
                                <tr>
                                    <th>Judul Modul</th>
                                    <th>Tipe</th>
                                    <th>Jenjang</th>
                                    <th>Level Kesulitan</th>
                                    <th>Pertanyaan</th>
                                    <th>Aksi</th>
                                </tr>
                            </thead>
                            <tbody>
                                {modules.map((module) => (
                                    <tr key={module.id} className="module-row">
                                        <td>
                                            <strong>{module.title}</strong>
                                            <div style={{ fontSize: '0.875rem', color: '#666' }}>
                                                {module.description}
                                            </div>
                                        </td>
                                        <td>
                                            <span className={`badge badge-${module.module_type}`}>
                                                {module.module_type}
                                            </span>
                                        </td>
                                        <td>
                                            <span className="badge" style={{ background: '#f3f4f6', color: '#374151' }}>
                                                {module.education_level}
                                            </span>
                                        </td>
                                        <td>Level {module.difficulty_level}</td>
                                        <td>{module.total_questions} Soal</td>
                                        <td>
                                            <div className="action-buttons">
                                                <button
                                                    className="btn-icon btn-edit"
                                                    onClick={() => navigate(`/teacher/modules/${module.id}/edit`)}
                                                    title="Edit"
                                                >
                                                    ✏️
                                                </button>
                                                <button
                                                    className="btn-icon btn-delete"
                                                    onClick={() => handleDelete(module.id)}
                                                    title="Hapus"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </main>
        </div>
    );
}
