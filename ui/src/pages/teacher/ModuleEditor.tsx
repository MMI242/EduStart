import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '../../components/Button';
import { modulesApi } from '../../api/modules';
import type { ModuleCreate, Question } from '../../api/modules';
import './ModuleEditor.css';

const QUESTION_TYPES = [
    { value: 'multiple_choice', label: 'Pilihan Ganda' },
    { value: 'matching', label: 'Mencocokkan Pasangan' },
    // { value: 'drag_drop', label: 'Drag & Drop' }, // Future implementation
];

const EDUCATION_LEVELS = [
    { value: 'TK', label: 'TK (Taman Kanak-kanak)' },
    { value: 'SD1', label: 'SD Kelas 1' },
    { value: 'SD2', label: 'SD Kelas 2' },
    { value: 'SD3', label: 'SD Kelas 3' },
    { value: 'SD4', label: 'SD Kelas 4' },
    { value: 'SD5', label: 'SD Kelas 5' },
    { value: 'SD6', label: 'SD Kelas 6' },
    { value: 'SMP', label: 'SMP' },
    { value: 'SMA', label: 'SMA' },
];

const INITIAL_QUESTION: Question = {
    id: '',
    question_text: '',
    question_type: 'multiple_choice',
    options: ['', '', '', ''],
    correct_answer: '',
    points: 10
};

export function ModuleEditor() {
    const navigate = useNavigate();
    const { moduleId } = useParams<{ moduleId: string }>();
    const isEditing = !!moduleId;

    const [isLoading, setIsLoading] = useState(false);
    // Combine ModuleCreate with optional id for local state
    const [moduleData, setModuleData] = useState<Partial<ModuleCreate & { id: string }>>({
        title: '',
        description: '',
        module_type: 'quiz',
        education_level: 'TK',
        difficulty_level: 1,
        estimated_duration_minutes: 10,
        content: {
            questions: [] as Question[]
        }
    });

    useEffect(() => {
        if (isEditing && moduleId) {
            loadModule();
        }
    }, [moduleId]);

    const loadModule = async () => {
        if (!moduleId) return;
        setIsLoading(true);
        try {
            const data = await modulesApi.getById(moduleId);
            // Transform ModuleDetail (flat questions) to ModuleCreate structure (nested content)
            setModuleData({
                id: data.id,
                title: data.title,
                description: data.description,
                module_type: data.type, // Map 'type' from backend to 'module_type'
                education_level: data.education_level,
                difficulty_level: data.difficulty_level,
                estimated_duration_minutes: data.estimated_duration_minutes,
                thumbnail_url: data.thumbnail_url,
                content: {
                    questions: data.questions,
                    learning_objectives: data.learning_objectives
                }
            });
        } catch (error) {
            console.error('Failed to load module:', error);
            alert('Gagal memuat modul');
            navigate('/teacher/dashboard');
        } finally {
            setIsLoading(false);
        }
    };

    const handleModuleChange = (field: string, value: any) => {
        setModuleData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleAddQuestion = () => {
        const newQuestion: Question = {
            ...INITIAL_QUESTION,
            id: Date.now().toString(), // Temporary ID
        };

        setModuleData(prev => ({
            ...prev,
            content: {
                ...prev.content,
                questions: [...(prev.content?.questions || []), newQuestion]
            }
        }));
    };

    const handleRemoveQuestion = (index: number) => {
        setModuleData(prev => {
            const newQuestions = [...(prev.content?.questions || [])];
            newQuestions.splice(index, 1);
            return {
                ...prev,
                content: {
                    ...prev.content,
                    questions: newQuestions
                }
            };
        });
    };

    const handleQuestionChange = (index: number, field: keyof Question, value: any) => {
        setModuleData(prev => {
            const newQuestions = [...(prev.content?.questions || [])];
            newQuestions[index] = {
                ...newQuestions[index],
                [field]: value
            };
            return {
                ...prev,
                content: {
                    ...prev.content,
                    questions: newQuestions
                }
            };
        });
    };

    const handleOptionChange = (qIndex: number, oIndex: number, value: string) => {
        setModuleData(prev => {
            const newQuestions = [...(prev.content?.questions || [])];
            const newOptions = [...(newQuestions[qIndex].options || [])];
            newOptions[oIndex] = value;
            newQuestions[qIndex] = {
                ...newQuestions[qIndex],
                options: newOptions
            };
            return {
                ...prev,
                content: {
                    ...prev.content,
                    questions: newQuestions
                }
            };
        });
    };

    const handleMatchingPairChange = (qIndex: number, pIndex: number, side: 'left' | 'right', value: string) => {
        setModuleData(prev => {
            const newQuestions = [...(prev.content?.questions || [])];
            const currentPairs = newQuestions[qIndex].matching_pairs || [];
            const newPairs = [...currentPairs];

            if (!newPairs[pIndex]) {
                newPairs[pIndex] = { left: '', right: '' };
            }

            newPairs[pIndex] = {
                ...newPairs[pIndex],
                [side]: value
            };

            newQuestions[qIndex] = {
                ...newQuestions[qIndex],
                matching_pairs: newPairs
            };

            return {
                ...prev,
                content: {
                    ...prev.content,
                    questions: newQuestions
                }
            };
        });
    };

    const addMatchingPair = (qIndex: number) => {
        setModuleData(prev => {
            const newQuestions = [...(prev.content?.questions || [])];
            const currentPairs = newQuestions[qIndex].matching_pairs || [];
            newQuestions[qIndex] = {
                ...newQuestions[qIndex],
                matching_pairs: [...currentPairs, { left: '', right: '' }]
            };
            return {
                ...prev,
                content: {
                    ...prev.content,
                    questions: newQuestions
                }
            };
        });
    };

    const removeMatchingPair = (qIndex: number, pIndex: number) => {
        setModuleData(prev => {
            const newQuestions = [...(prev.content?.questions || [])];
            const newPairs = [...(newQuestions[qIndex].matching_pairs || [])];
            newPairs.splice(pIndex, 1);
            newQuestions[qIndex] = {
                ...newQuestions[qIndex],
                matching_pairs: newPairs
            };
            return {
                ...prev,
                content: {
                    ...prev.content,
                    questions: newQuestions
                }
            };
        });
    };

    const handleSave = async () => {
        setIsLoading(true);
        try {
            // Validation basic
            if (!moduleData.title || !moduleData.content?.questions?.length) {
                alert('Judul dan minimal 1 pertanyaan harus diisi');
                return;
            }

            if (isEditing && moduleId) {
                // For update, we can pass moduleData as ModuleUpdate
                await modulesApi.update(moduleId, moduleData);
            } else {
                // For create, we need to ensure id is not present if it was accidentally set
                const { id, ...createData } = moduleData;
                await modulesApi.create(createData as ModuleCreate);
            }
            navigate('/teacher/dashboard');
        } catch (error) {
            console.error('Failed to save module:', error);
            alert('Gagal menyimpan modul');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading && isEditing && !moduleData.id) {
        return <div className="loading">Memuat...</div>;
    }

    return (
        <div className="module-editor">
            <header className="editor-header">
                <div className="header-left">
                    <Button variant="ghost" onClick={() => navigate('/teacher/dashboard')}>
                        ← Kembali
                    </Button>
                    <h1>{isEditing ? 'Edit Modul' : 'Buat Modul Baru'}</h1>
                </div>
                <div className="header-actions">
                    <Button variant="primary" onClick={handleSave} disabled={isLoading}>
                        {isLoading ? 'Menyimpan...' : 'Simpan Modul'}
                    </Button>
                </div>
            </header>

            <div className="editor-container">
                <section className="editor-form" id="module-details">
                    <h3>Informasi Dasar</h3>
                    <div className="form-group">
                        <label>Judul Modul</label>
                        <input
                            type="text"
                            className="form-input"
                            value={moduleData.title}
                            onChange={(e) => handleModuleChange('title', e.target.value)}
                            placeholder="Contoh: Belajar Angka Dasar"
                        />
                    </div>

                    <div className="form-group">
                        <label>Deskripsi</label>
                        <textarea
                            className="form-textarea"
                            value={moduleData.description}
                            onChange={(e) => handleModuleChange('description', e.target.value)}
                            rows={3}
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Tipe Modul</label>
                            <select
                                className="form-select"
                                value={moduleData.module_type}
                                onChange={(e) => handleModuleChange('module_type', e.target.value)}
                            >
                                <option value="quiz">Kuis Interaktif</option>
                                <option value="video">Video Pembelajaran</option>
                                <option value="game">Game Edukasi</option>
                            </select>
                        </div>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Jenjang Pendidikan</label>
                            <select
                                className="form-select"
                                value={moduleData.education_level}
                                onChange={(e) => handleModuleChange('education_level', e.target.value)}
                            >
                                {EDUCATION_LEVELS.map(level => (
                                    <option key={level.value} value={level.value}>
                                        {level.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Tingkat Kesulitan (1-10)</label>
                            <input
                                type="number"
                                className="form-input"
                                min="1" max="10"
                                value={moduleData.difficulty_level}
                                onChange={(e) => handleModuleChange('difficulty_level', parseInt(e.target.value))}
                            />
                        </div>
                    </div>
                </section>

                <section className="questions-section">
                    <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <h3>Daftar Pertanyaan</h3>
                        <Button variant="outline" onClick={handleAddQuestion}>
                            + Tambah Pertanyaan
                        </Button>
                    </div>

                    <div className="question-list">
                        {moduleData.content?.questions?.map((question, qIndex) => (
                            <div key={qIndex} className="question-item">
                                <div className="question-header">
                                    <span className="question-number">No. {qIndex + 1}</span>
                                    <Button
                                        variant="ghost"
                                        className="btn-delete-question"
                                        onClick={() => handleRemoveQuestion(qIndex)}
                                        style={{ color: 'red' }}
                                    >
                                        Hapus Soal
                                    </Button>
                                </div>

                                <div className="form-group">
                                    <label>Tipe Pertanyaan</label>
                                    <select
                                        className="form-select"
                                        value={question.question_type}
                                        onChange={(e) => handleQuestionChange(qIndex, 'question_type', e.target.value)}
                                    >
                                        {QUESTION_TYPES.map(type => (
                                            <option key={type.value} value={type.value}>
                                                {type.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Pertanyaan</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={question.question_text}
                                        onChange={(e) => handleQuestionChange(qIndex, 'question_text', e.target.value)}
                                        placeholder="Tulis pertanyaan di sini..."
                                    />
                                </div>

                                {question.question_type === 'matching' ? (
                                    <div className="matching-pairs-editor">
                                        <label>Pasangan Jawaban (Kiri - Kanan)</label>
                                        {question.matching_pairs?.map((pair, pIndex) => (
                                            <div key={pIndex} className="pair-row">
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    placeholder="Sisi Kiri"
                                                    value={pair.left}
                                                    onChange={(e) => handleMatchingPairChange(qIndex, pIndex, 'left', e.target.value)}
                                                />
                                                <span className="pair-arrow">↔️</span>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    placeholder="Sisi Kanan"
                                                    value={pair.right}
                                                    onChange={(e) => handleMatchingPairChange(qIndex, pIndex, 'right', e.target.value)}
                                                />
                                                <Button
                                                    variant="ghost"
                                                    onClick={() => removeMatchingPair(qIndex, pIndex)}
                                                >
                                                    ❌
                                                </Button>
                                            </div>
                                        ))}
                                        {(!question.matching_pairs || question.matching_pairs.length < 5) && (
                                            <Button variant="outline" onClick={() => addMatchingPair(qIndex)} size="sm">
                                                + Tambah Pasangan
                                            </Button>
                                        )}
                                    </div>
                                ) : (
                                    <div className="options-editor">
                                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                                            <label>Pilihan Jawaban (Klik radio untuk set kunci jawaban)</label>
                                        </div>
                                        {question.options?.map((option, oIndex) => (
                                            <div key={oIndex} className="option-item">
                                                <input
                                                    type="radio"
                                                    name={`correct-${qIndex}`}
                                                    checked={question.correct_answer === option && option !== ''}
                                                    onChange={() => handleQuestionChange(qIndex, 'correct_answer', option)}
                                                    className="correct-radio"
                                                />
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={option}
                                                    onChange={(e) => handleOptionChange(qIndex, oIndex, e.target.value)}
                                                    placeholder={`Pilihan ${String.fromCharCode(65 + oIndex)}`}
                                                />
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
}
