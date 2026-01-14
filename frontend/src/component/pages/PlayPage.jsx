import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';

// Narrative Typing Effect Component
const DramaticText = ({ text, onComplete }) => {
    const [displayedText, setDisplayedText] = useState('');
    const indexRef = useRef(0);

    useEffect(() => {
        setDisplayedText('');
        indexRef.current = 0;

        const speed = 20; // Faster typing speed (20ms per char)

        const timer = setInterval(() => {
            if (indexRef.current < text.length) {
                setDisplayedText((prev) => prev + text.charAt(indexRef.current));
                indexRef.current++;
            } else {
                clearInterval(timer);
                onComplete?.();
            }
        }, speed);

        return () => clearInterval(timer);
    }, [text]);

    return (
        <div className="relative">
            <p className="text-lg leading-relaxed whitespace-pre-line text-gray-200" style={{ fontFamily: 'var(--font-body)' }}>
                {displayedText}
                <span className="inline-block w-2 h-5 ml-1 align-middle bg-[#facc15] animate-pulse" />
            </p>
        </div>
    );
};

const PlayPage = () => {
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [choices, setChoices] = useState([]);
    const [stats, setStats] = useState({ hp: 100, maxHp: 100, level: 1, exp: 0, location: '', inventory: [] });
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showInventory, setShowInventory] = useState(false);
    const [showTurnPanel, setShowTurnPanel] = useState(false);
    const [revealingIndex, setRevealingIndex] = useState(-1);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, revealingIndex]);

    useEffect(() => {
        if (showTurnPanel && inputRef.current) {
            inputRef.current.focus();
        }
    }, [showTurnPanel]);

    useEffect(() => {
        initializeSession();
    }, []);

    const initializeSession = async () => {
        const savedSessionId = localStorage.getItem('dungeon_session_id');
        if (savedSessionId) {
            setLoading(true);
            try {
                const response = await fetch(`http://localhost:8000/game/${savedSessionId}`);
                if (response.ok) {
                    const data = await response.json();
                    applySessionData(data, true);
                    setLoading(false);
                    return;
                }
            } catch (error) {
                console.warn("Failed to restore session");
            }
        }
        startNewGame();
    };

    const applySessionData = (data, skipAnimation = false) => {
        setSessionId(data.id);
        localStorage.setItem('dungeon_session_id', data.id);
        setMessages(data.messages || []);
        setChoices(data.choices || []);
        setStats({
            hp: data.hp,
            maxHp: data.max_hp,
            level: data.level,
            exp: data.exp,
            location: data.location,
            inventory: data.inventory
        });

        if (skipAnimation) {
            setRevealingIndex(data.messages?.length || 0);
        } else {
            // Start revealing from the last message
            setRevealingIndex((data.messages?.length || 1) - 1);
        }
    };

    const startNewGame = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/game/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ starting_scenario: "You stand at the entrance of a dark, ominous dungeon." }),
            });
            const data = await response.json();
            applySessionData(data);
        } catch (error) {
            console.error('Error starting game:', error);
            setMessages([{ role: 'system', content: "Failed to connect to the server." }]);
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async (actionText = null) => {
        const action = actionText || input;
        if (!action.trim() || !sessionId || loading) return;

        setInput('');
        setLoading(true);
        setShowTurnPanel(false);

        try {
            const response = await fetch('http://localhost:8000/game/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, action }),
            });

            if (!response.ok) throw new Error('Action failed');

            const data = await response.json();
            applySessionData(data);

            if (data.game_over) {
                setMessages(prev => [...prev, { role: 'system', content: "GAME OVER" }]);
            }

        } catch (error) {
            console.error('Error:', error);
            setMessages(prev => [...prev, { role: 'system', content: "Something went wrong." }]);
        } finally {
            setLoading(false);
        }
    };

    const handleUndo = async () => {
        if (!sessionId || loading) return;
        setLoading(true);
        setShowTurnPanel(false);
        try {
            const response = await fetch('http://localhost:8000/game/undo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId }),
            });
            if (response.ok) {
                const data = await response.json();
                applySessionData(data, true);
            }
        } catch (error) {
            console.error('Undo failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const resetGame = () => {
        localStorage.removeItem('dungeon_session_id');
        window.location.reload();
    };

    const handleTakeTurn = () => {
        setShowTurnPanel(!showTurnPanel);
        setInput('');
    };

    const handleChoiceClick = (choice) => {
        setInput(choice);
        if (inputRef.current) {
            inputRef.current.focus();
        }
    };

    const handleSubmitTurn = (e) => {
        e?.preventDefault();
        if (input.trim()) {
            handleSend(input);
        }
    };

    // Helper to keep scrolling during typing
    // We can use a custom interval to scroll to bottom while typing is active if needed.
    // For now simple ref scroll on completion/message add is fine.

    return (
        <div className="min-h-screen bg-[#0a0f1a] relative">
            {/* Background */}
            <div
                className="fixed inset-0 opacity-20 bg-cover bg-center pointer-events-none"
                style={{
                    backgroundImage: 'linear-gradient(to bottom, rgba(10, 15, 26, 0.5), rgba(10, 15, 26, 1))'
                }}
            />

            {/* Top Bar */}
            <div className="fixed top-0 left-0 right-0 z-50 flex justify-between items-center px-6 py-4 bg-[#0a0f1a]/90 backdrop-blur-md border-b border-white/5">
                <div className="flex items-center gap-6">
                    <Link to="/" className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
                        <span className="text-xl">⚔</span>
                        <span className="font-medium" style={{ fontFamily: 'var(--font-display)' }}>AI Dungeon</span>
                    </Link>
                    <button
                        onClick={() => setShowInventory(!showInventory)}
                        className="flex items-center gap-2 text-gray-400 hover:text-[#facc15] transition-colors"
                    >
                        <span>🎒</span>
                        <span className="text-sm">{stats.inventory?.length || 0}</span>
                    </button>
                </div>
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span>HP: <span className={stats.hp > 50 ? 'text-emerald-400' : stats.hp > 25 ? 'text-yellow-400' : 'text-red-400'}>{stats.hp}/{stats.maxHp}</span></span>
                        <span>Lv.<span className="text-[#facc15]">{stats.level}</span></span>
                    </div>
                    <button onClick={handleUndo} className="text-gray-500 hover:text-white transition-colors">↺</button>
                    <button onClick={resetGame} className="text-gray-500 hover:text-red-400 transition-colors">⟲</button>
                </div>
            </div>

            {/* Inventory Dropdown */}
            {showInventory && (
                <div className="fixed top-16 left-6 z-40 bg-[#0f172a]/95 backdrop-blur-md rounded-lg border border-[#facc15]/20 p-4 w-64 shadow-xl">
                    <h3 className="text-[#facc15] text-sm font-semibold mb-3" style={{ fontFamily: 'var(--font-display)' }}>🎒 Inventory</h3>
                    {stats.inventory?.length > 0 ? (
                        <ul className="space-y-2">
                            {stats.inventory.map((item, index) => (
                                <li key={index} className="text-gray-300 text-sm">• {item}</li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-500 text-sm italic">Empty</p>
                    )}
                </div>
            )}

            {/* Main Content - Dramatic Text */}
            <div className="relative z-10 max-w-3xl mx-auto px-6 pt-24 pb-52">
                <div className="space-y-10">
                    {messages.map((msg, index) => (
                        <div key={index}>
                            {msg.role === 'user' ? (
                                /* Player Action - Right aligned */
                                <div className={`text-right transition-all duration-500 ${index <= revealingIndex ? 'opacity-100' : 'opacity-0'}`}>
                                    <p className="text-gray-500 italic text-base">
                                        ✦ {msg.content}
                                    </p>
                                </div>
                            ) : msg.role === 'system' ? (
                                /* System Message */
                                <div className={`text-center py-8 transition-all duration-500 ${index <= revealingIndex ? 'opacity-100' : 'opacity-0'}`}>
                                    <p className="text-red-400 font-bold text-2xl tracking-widest" style={{ fontFamily: 'var(--font-display)' }}>
                                        {msg.content}
                                    </p>
                                </div>
                            ) : (
                                /* Dungeon Master - Dramatic reveal */
                                <div className="text-left text-gray-200">
                                    {index === revealingIndex ? (
                                        <DramaticText
                                            text={msg.content}
                                            onComplete={() => setRevealingIndex(index + 1)}
                                        />
                                    ) : index < revealingIndex ? (
                                        <p className="text-lg leading-relaxed whitespace-pre-line opacity-80" style={{ fontFamily: 'var(--font-body)' }}>
                                            {msg.content}
                                        </p>
                                    ) : null}
                                </div>
                            )}
                        </div>
                    ))}

                    {loading && (
                        <div className="text-left">
                            <p className="text-gray-600 italic animate-pulse">The tale unfolds...</p>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Bottom Action Bar */}
            <div className="fixed bottom-0 left-0 right-0 z-50 bg-gradient-to-t from-[#0a0f1a] via-[#0a0f1a]/95 to-transparent pt-12 pb-6">
                <div className="max-w-3xl mx-auto px-6">
                    {/* Turn Panel */}
                    {showTurnPanel && !loading && (
                        <div className="mb-4 animate-fadeIn">
                            {choices.length > 0 && (
                                <div className="flex flex-wrap justify-center gap-2 mb-3">
                                    {choices.map((choice, index) => (
                                        <button
                                            key={index}
                                            onClick={() => handleChoiceClick(choice)}
                                            className={`px-3 py-1.5 text-sm border rounded-full transition-all ${input === choice
                                                ? 'border-[#facc15] text-[#facc15] bg-[#facc15]/10'
                                                : 'border-gray-700 text-gray-500 hover:border-gray-500 hover:text-gray-400'
                                                }`}
                                        >
                                            {choice}
                                        </button>
                                    ))}
                                </div>
                            )}
                            <form onSubmit={handleSubmitTurn} className="flex gap-2">
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="What do you want to do?"
                                    className="flex-1 px-4 py-3 bg-[#1e293b]/50 border border-gray-700 rounded-full text-gray-200 placeholder-gray-600 focus:outline-none focus:border-[#facc15]/50 transition-all"
                                />
                                <button
                                    type="submit"
                                    disabled={!input.trim()}
                                    className="px-6 py-3 bg-[#facc15] text-[#0a0f1a] font-semibold rounded-full hover:bg-[#facc15]/90 transition-all disabled:opacity-30"
                                    style={{ fontFamily: 'var(--font-display)' }}
                                >
                                    GO
                                </button>
                            </form>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex justify-center gap-3">
                        <button
                            onClick={handleTakeTurn}
                            disabled={loading}
                            className={`flex items-center gap-2 px-5 py-2.5 border rounded-full text-sm font-medium transition-all disabled:opacity-50 ${showTurnPanel
                                ? 'bg-[#facc15]/20 border-[#facc15] text-[#facc15]'
                                : 'bg-transparent border-[#facc15]/30 text-[#facc15] hover:bg-[#facc15]/10'
                                }`}
                        >
                            ✏️ TAKE A TURN
                        </button>
                        <button
                            onClick={() => handleSend("Continue")}
                            disabled={loading}
                            className="px-5 py-2.5 bg-transparent border border-gray-700 rounded-full text-gray-400 text-sm font-medium hover:bg-white/5 transition-all disabled:opacity-50"
                        >
                            ✦ CONTINUE
                        </button>
                        <button
                            onClick={handleUndo}
                            disabled={loading}
                            className="px-5 py-2.5 bg-transparent border border-gray-700 rounded-full text-gray-400 text-sm font-medium hover:bg-white/5 transition-all disabled:opacity-50"
                        >
                            ↺ RETRY
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PlayPage;
