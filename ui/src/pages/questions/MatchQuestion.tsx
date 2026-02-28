import { useState, useEffect, useCallback } from 'react';
import './MatchQuestion.css';

interface MatchPair {
    left: string;
    right: string;
}

interface MatchQuestionProps {
    pairs: MatchPair[];
    onComplete: (isCorrect: boolean) => void;
}

interface ItemState {
    id: string;
    text: string;
    type: 'left' | 'right';
    state: 'idle' | 'selected' | 'matched' | 'wrong';
    pairId: string; // The ID of the pair this item belongs to (usually the left item's text or a unique ID)
}

function buildItems(pairs: MatchPair[]) {
    const left: ItemState[] = pairs.map((pair, index) => ({
        id: `left-${index}`,
        text: pair.left,
        type: 'left' as const,
        state: 'idle' as const,
        pairId: `pair-${index}`
    }));

    const right: ItemState[] = pairs.map((pair, index) => ({
        id: `right-${index}`,
        text: pair.right,
        type: 'right' as const,
        state: 'idle' as const,
        pairId: `pair-${index}`
    }));

    // Shuffle right items
    const shuffledRight = [...right].sort(() => Math.random() - 0.5);

    return { left, right: shuffledRight };
}

export function MatchQuestion({ pairs, onComplete }: MatchQuestionProps) {
    const [leftItems, setLeftItems] = useState<ItemState[]>(() => buildItems(pairs).left);
    const [rightItems, setRightItems] = useState<ItemState[]>(() => buildItems(pairs).right);
    const [selectedLeft, setSelectedLeft] = useState<string | null>(null);
    const [selectedRight, setSelectedRight] = useState<string | null>(null);
    const [isWrong, setIsWrong] = useState(false);

    const checkMatch = useCallback((leftId: string, rightId: string) => {
        const leftItem = leftItems.find(i => i.id === leftId);
        const rightItem = rightItems.find(i => i.id === rightId);

        if (!leftItem || !rightItem) return;

        if (leftItem.pairId === rightItem.pairId) {
            // Match found!
            setLeftItems(prev => prev.map(i => i.id === leftId ? { ...i, state: 'matched' } : i));
            setRightItems(prev => prev.map(i => i.id === rightId ? { ...i, state: 'matched' } : i));
            setSelectedLeft(null);
            setSelectedRight(null);
        } else {
            // Wrong match
            setIsWrong(true);
            setTimeout(() => {
                setIsWrong(false);
                setSelectedLeft(null);
                setSelectedRight(null);
            }, 1000);
        }
    }, [leftItems, rightItems]);

    const handleItemClick = (item: ItemState) => {
        if (item.state === 'matched' || isWrong) return;

        if (item.type === 'left') {
            if (selectedLeft === item.id) {
                setSelectedLeft(null);
            } else {
                // If right is already selected, check match immediately
                if (selectedRight) {
                    setSelectedLeft(item.id);
                    checkMatch(item.id, selectedRight);
                } else {
                    setSelectedLeft(item.id);
                }
            }
        } else {
            if (selectedRight === item.id) {
                setSelectedRight(null);
            } else {
                // If left is already selected, check match immediately
                if (selectedLeft) {
                    setSelectedRight(item.id);
                    checkMatch(selectedLeft, item.id);
                } else {
                    setSelectedRight(item.id);
                }
            }
        }
    };

    // Check completion
    useEffect(() => {
        if (leftItems.length > 0 && leftItems.every(i => i.state === 'matched')) {
            // Add a small delay for visual satisfaction
            setTimeout(() => {
                onComplete(true);
            }, 500);
        }
    }, [leftItems, onComplete]);

    const getItemClassName = (item: ItemState, isSelected: boolean) => {
        let className = 'match-item';
        if (item.state === 'matched') className += ' matched';
        if (isSelected) className += ' selected';
        if (isSelected && isWrong) className += ' wrong';
        return className;
    };

    return (
        <div className="match-question-container">
            <div className="match-column left-column">
                {leftItems.map(item => (
                    <div
                        key={item.id}
                        className={getItemClassName(item, selectedLeft === item.id)}
                        onClick={() => handleItemClick(item)}
                    >
                        {item.text}
                    </div>
                ))}
            </div>
            <div className="match-column right-column">
                {rightItems.map(item => (
                    <div
                        key={item.id}
                        className={getItemClassName(item, selectedRight === item.id)}
                        onClick={() => handleItemClick(item)}
                    >
                        {item.text}
                    </div>
                ))}
            </div>
        </div>
    );
}
