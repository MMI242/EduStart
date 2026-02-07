import { useState, useEffect } from 'react';
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

export function MatchQuestion({ pairs, onComplete }: MatchQuestionProps) {
    const [leftItems, setLeftItems] = useState<ItemState[]>([]);
    const [rightItems, setRightItems] = useState<ItemState[]>([]);
    const [selectedLeft, setSelectedLeft] = useState<string | null>(null);
    const [selectedRight, setSelectedRight] = useState<string | null>(null);
    const [isWrong, setIsWrong] = useState(false);

    // Initialize and shuffle items
    useEffect(() => {
        const left: ItemState[] = pairs.map((pair, index) => ({
            id: `left-${index}`,
            text: pair.left,
            type: 'left',
            state: 'idle',
            pairId: `pair-${index}`
        }));

        const right: ItemState[] = pairs.map((pair, index) => ({
            id: `right-${index}`,
            text: pair.right,
            type: 'right',
            state: 'idle',
            pairId: `pair-${index}`
        }));

        // Shuffle right items
        const shuffledRight = [...right].sort(() => Math.random() - 0.5);

        setLeftItems(left);
        setRightItems(shuffledRight);
    }, [pairs]);

    const handleItemClick = (item: ItemState) => {
        if (item.state === 'matched' || isWrong) return;

        if (item.type === 'left') {
            if (selectedLeft === item.id) {
                // Deselect
                setSelectedLeft(null);
            } else {
                setSelectedLeft(item.id);
            }
        } else {
            if (selectedRight === item.id) {
                // Deselect
                setSelectedRight(null);
            } else {
                setSelectedRight(item.id);
            }
        }
    };

    // Check for match
    useEffect(() => {
        if (selectedLeft && selectedRight) {
            checkMatch();
        }
    }, [selectedLeft, selectedRight]);

    const checkMatch = () => {
        const leftItem = leftItems.find(i => i.id === selectedLeft);
        const rightItem = rightItems.find(i => i.id === selectedRight);

        if (!leftItem || !rightItem) return;

        if (leftItem.pairId === rightItem.pairId) {
            // Match found!
            setLeftItems(prev => prev.map(i => i.id === selectedLeft ? { ...i, state: 'matched' } : i));
            setRightItems(prev => prev.map(i => i.id === selectedRight ? { ...i, state: 'matched' } : i));
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
