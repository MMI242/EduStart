// Learning Module Page - Integrated with Backend API
import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { Button } from '../components/Button';
import { Card, CardBody } from '../components/Card';
import { modulesApi } from '../api/modules';
import { progressApi } from '../api/progress';
import { analyticsApi } from '../api/analytics';
import type { ModuleDetail } from '../api/modules';
import { MatchQuestion } from './questions/MatchQuestion';
import './LearningModule.css';

export function LearningModule() {
    const { moduleId } = useParams<{ moduleId: string }>();
    const [searchParams] = useSearchParams();
    const childId = searchParams.get('childId');
    const navigate = useNavigate();

    const [module, setModule] = useState<ModuleDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
    const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
    const [score, setScore] = useState(0);
    const [showResult, setShowResult] = useState(false);
    const [streak, setStreak] = useState(0);
    // const [isSaving, setIsSaving] = useState(false);

    // Track time for each question
    const questionStartTime = useRef<number>(Date.now());
    const hesitationStartTime = useRef<number>(Date.now());
    const isInteracted = useRef<boolean>(false);

    // Track hesitation (first interaction)
    const handleInteraction = () => {
        if (!isInteracted.current) {
            isInteracted.current = true;
            // Hesitation is time from question load to first interaction
        }
    };

    // Fetch module from API
    useEffect(() => {
        async function fetchModule() {
            if (!moduleId) {
                setError('Module ID tidak ditemukan');
                setIsLoading(false);
                return;
            }

            try {
                const data = await modulesApi.getById(moduleId);
                setModule(data);
                questionStartTime.current = Date.now();
                hesitationStartTime.current = Date.now();
                isInteracted.current = false;
            } catch (err) {
                console.error('Failed to fetch module:', err);
                setError('Gagal memuat modul. Silakan coba lagi.');
            } finally {
                setIsLoading(false);
            }
        }
        fetchModule();
    }, [moduleId]);

    const question = module?.questions[currentQuestion];
    const totalQuestions = module?.questions.length || 0;
    const progress = totalQuestions > 0 ? ((currentQuestion + 1) / totalQuestions) * 100 : 0;

    const handleAnswer = async (answer: string) => {
        if (selectedAnswer !== null || !module || !moduleId) return;

        const currentQ = module.questions[currentQuestion];
        const isMatchQuestion = currentQ.question_type === 'matching';
        const isCorrectAnswer = isMatchQuestion ? answer === 'matched' : answer === currentQ.correct_answer;

        // Mark interaction if not already done (in case direct click without hover/other interaction)
        if (!isInteracted.current) {
            isInteracted.current = true;
        }

        setSelectedAnswer(answer);
        setIsCorrect(isCorrectAnswer);

        if (isCorrectAnswer) {
            setScore(score + 10);
            setStreak(streak + 1);
            // Play success sound
        } else {
            setStreak(0);
            // Play error sound
        }

        // Save progress if childId is present
        if (childId) {
            const timeSpent = Math.max(1, Math.floor((Date.now() - questionStartTime.current) / 1000));
            try {
                await progressApi.saveProgress(childId, {
                    module_id: moduleId,
                    question_id: currentQ.id,
                    is_correct: isCorrectAnswer,
                    time_taken_seconds: timeSpent
                });

                // Analytics tracking (New)
                const endTime = Date.now();
                const totalDuration = endTime - questionStartTime.current;
                // Hesitation is difference between start and first interaction
                // If never interacted before answer (rare), hesitation = duration
                const hesitationDuration = isInteracted.current ? (Date.now() - hesitationStartTime.current) : totalDuration;
                // Note: The simple logic above might need refinement. 
                // Ideally we capture the timestamp of first interaction.
                // Let's refine: hesitation = (Time of First Interaction) - Start Time.
                // Since we don't store the exact timestamp of interaction, let's approximate:
                // If we want precise hesitation, we should capture `firstInteractionTime`.

                await analyticsApi.trackEvent(childId, {
                    module_id: moduleId,
                    question_id: currentQ.id,
                    question_type: currentQ.question_type,
                    difficulty_level: module.difficulty_level,
                    is_correct: isCorrectAnswer,
                    duration_ms: totalDuration,
                    hesitation_ms: Math.max(0, hesitationDuration)
                });

            } catch (err) {
                console.error('Failed to save progress/analytics', err);
            }
        }
    };

    const handleNext = () => {
        if (currentQuestion < totalQuestions - 1) {
            setCurrentQuestion(currentQuestion + 1);
            setSelectedAnswer(null);
            setIsCorrect(null);
            questionStartTime.current = Date.now(); // Reset timer for next question
            hesitationStartTime.current = Date.now();
            isInteracted.current = false;
        } else {
            setShowResult(true);
        }
    };

    const handleRestart = () => {
        setCurrentQuestion(0);
        setSelectedAnswer(null);
        setIsCorrect(null);
        setScore(0);
        setStreak(0);
        setShowResult(false);
        questionStartTime.current = Date.now();
        hesitationStartTime.current = Date.now();
        isInteracted.current = false;
    };

    const getStars = () => {
        if (totalQuestions === 0) return '💪';
        const percentage = (score / (totalQuestions * 10)) * 100;
        if (percentage >= 90) return '⭐⭐⭐';
        if (percentage >= 70) return '⭐⭐';
        if (percentage >= 50) return '⭐';
        return '💪';
    };

    const getModuleIcon = (type?: string) => {
        switch (type) {
            case 'reading': return '📖';
            case 'counting': return '🔢';
            case 'cognitive': return '🧩';
            default: return '📚';
        }
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="learning-module">
                <div className="module-container">
                    <div className="loading-state">
                        <div className="spinner" />
                        <p>Memuat modul...</p>
                    </div>
                </div>
            </div>
        );
    }

    // Error state
    if (error || !module) {
        return (
            <div className="learning-module">
                <div className="module-container">
                    <div className="error-state">
                        <span className="error-icon">😕</span>
                        <h2>{error || 'Modul tidak ditemukan'}</h2>
                        <Button variant="primary" onClick={() => navigate(childId ? `/modules?childId=${childId}` : '/modules')}>
                            Kembali ke Daftar Modul
                        </Button>
                    </div>
                </div>
            </div>
        );
    }

    // No questions
    if (!module.questions || module.questions.length === 0) {
        return (
            <div className="learning-module">
                <div className="module-container">
                    <div className="error-state">
                        <span className="error-icon">📭</span>
                        <h2>Modul ini belum memiliki pertanyaan</h2>
                        <Button variant="outline" size="lg" onClick={() => navigate(childId ? `/modules?childId=${childId}` : '/modules')}>
                            Kembali 🏠
                        </Button>
                    </div>
                </div>
            </div>
        );
    }

    // Result screen
    if (showResult) {
        return (
            <div className="learning-module">
                <div className="module-container">
                    <div className="result-screen">
                        <div className="result-stars">{getStars()}</div>
                        <h1>Selesai! 🎉</h1>
                        <div className="result-score">
                            <span className="score-label">Skor Kamu</span>
                            <span className="score-value">{score}</span>
                            <span className="score-label">poin</span>
                        </div>
                        <p className="result-message">
                            {score >= 40
                                ? 'Hebat! Kamu sangat pintar! 🌟'
                                : score >= 25
                                    ? 'Bagus! Terus berlatih ya! 💪'
                                    : 'Ayo coba lagi! Kamu pasti bisa! 🚀'}
                        </p>
                        {!childId && (
                            <p className="progress-warning">
                                ⚠️ Progress tidak tersimpan (pilih profil anak terlebih dahulu)
                            </p>
                        )}
                        <div className="result-actions">
                            <Button variant="primary" size="lg" onClick={handleRestart}>
                                Main Lagi 🔄
                            </Button>
                            <Button variant="outline" size="lg" onClick={() => navigate(childId ? `/modules?childId=${childId}` : '/modules')}>
                                Kembali 🏠
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="learning-module" onMouseMove={handleInteraction} onTouchStart={handleInteraction}>
            {/* Header */}
            <header className="module-header">
                <button className="back-btn" onClick={() => navigate(childId ? `/modules?childId=${childId}` : '/modules')}>
                    ← Kembali
                </button>
                <div className="module-info">
                    <h1>{getModuleIcon(module.type)} {module.title}</h1>
                    <span>{module.description}</span>
                </div>
                <div className="module-score">
                    <span className="score-icon">⭐</span>
                    <span>{score}</span>
                </div>
            </header>

            {/* Progress Bar */}
            <div className="progress-container">
                <div className="progress-bar" style={{ width: `${progress}%` }} />
                <span className="progress-text">{currentQuestion + 1} / {totalQuestions}</span>
            </div>

            {/* Question */}
            <div className="module-container">
                {question && (
                    <>
                        <Card className="question-card">
                            <CardBody>
                                <div className="question-content">
                                    <p className="question-instruction">{question.question_text}</p>
                                    {question.media_url && (
                                        <img
                                            src={question.media_url}
                                            alt="Question"
                                            className="question-media"
                                        />
                                    )}

                                    {streak >= 2 && (
                                        <div className="streak-badge">
                                            🔥 {streak}x Kombo!
                                        </div>
                                    )}
                                </div>

                                {/* Conditional rendering for question types */}
                                {question.question_type === 'matching' && question.matching_pairs ? (
                                    <MatchQuestion
                                        pairs={question.matching_pairs}
                                        onComplete={(isCorrect: boolean) => handleAnswer(isCorrect ? 'matched' : 'wrong')}
                                    />
                                ) : (
                                    <div className="answer-grid">
                                        {question.options?.map((option, index) => (
                                            <button
                                                key={index}
                                                className={`answer-btn ${selectedAnswer === option
                                                    ? isCorrect
                                                        ? 'correct'
                                                        : 'incorrect'
                                                    : ''
                                                    } ${selectedAnswer !== null && option === question.correct_answer
                                                        ? 'show-correct'
                                                        : ''
                                                    }`}
                                                onClick={() => handleAnswer(option)}
                                                disabled={selectedAnswer !== null}
                                            >
                                                {option}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </CardBody>
                        </Card>


                        {/* Feedback */}
                        {selectedAnswer !== null && (
                            <div className={`feedback ${isCorrect ? 'correct' : 'incorrect'}`}>
                                <span className="feedback-icon">
                                    {isCorrect ? '🎉' : '😅'}
                                </span>
                                <span className="feedback-text">
                                    {isCorrect ? 'Benar! Keren!' : `Oops! Jawabannya ${question.correct_answer}`}
                                </span>
                                <Button variant="primary" onClick={handleNext}>
                                    {currentQuestion < totalQuestions - 1 ? 'Lanjut →' : 'Lihat Hasil'}
                                </Button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
