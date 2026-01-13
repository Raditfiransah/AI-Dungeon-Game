import React, { useState, useEffect, useRef } from 'react';

const Homepage = () => {
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [choices, setChoices] = useState([]);
    const [stats, setStats] = useState({ hp: 100, maxHp: 100, level: 1, exp: 0, location: '', inventory: [] });
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

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
                    applySessionData(data);
                    setLoading(false);
                    return;
                }
            } catch (error) {
                console.warn("Failed to restore session");
            }
        }
        startNewGame();
    };

    const applySessionData = (data) => {
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

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || !sessionId || loading) return;

        const userAction = input;
        setInput('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/game/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, action: userAction }),
            });

            if (!response.ok) {
                throw new Error('Action failed');
            }

            const data = await response.json();
            setMessages(data.messages || []);
            setChoices(data.choices || []);
            setStats({
                hp: data.hp,
                maxHp: stats.maxHp,
                level: data.level,
                exp: data.exp,
                location: data.location,
                inventory: data.inventory
            });

            if (data.game_over) {
                setMessages(prev => [...prev, { role: 'system', content: "💀 GAME OVER 💀" }]);
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
        try {
            const response = await fetch('http://localhost:8000/game/undo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId }),
            });

            if (response.ok) {
                const data = await response.json();
                applySessionData(data);
            }
        } catch (error) {
            console.error('Undo failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleChoiceClick = (choice) => {
        setInput(choice);
    };

    const resetGame = () => {
        localStorage.removeItem('dungeon_session_id');
        window.location.reload();
    };

    // HP Bar color
    const hpPercent = (stats.hp / stats.maxHp) * 100;
    const hpColor = hpPercent > 60 ? 'bg-emerald-500' : hpPercent > 30 ? 'bg-yellow-500' : 'bg-red-500';

    return (
        <div className="flex justify-center items-start min-h-[calc(100vh-6rem)] pt-6 px-4">
            <div className="bg-[#1a1a1a] p-6 rounded-xl shadow-2xl w-full max-w-4xl border border-gray-800 flex flex-col h-[700px]">

                {/* Header with Stats */}
                <div className="mb-4 border-b border-gray-700 pb-4">
                    <div className="flex justify-between items-center mb-3">
                        <div>
                            <h2 className="text-2xl font-bold text-white">🏰 AI Dungeon</h2>
                            <p className="text-gray-400 text-sm">{stats.location}</p>
                        </div>
                        <button onClick={resetGame} className="text-xs text-red-400 hover:text-red-300 underline">
                            Reset Game
                        </button>
                    </div>

                    {/* Stats Bar */}
                    <div className="flex gap-4 items-center text-sm">
                        <div className="flex-1">
                            <div className="flex justify-between text-gray-400 mb-1">
                                <span>HP</span>
                                <span>{stats.hp}/{stats.maxHp}</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                                <div className={`${hpColor} h-2 rounded-full transition-all`} style={{ width: `${hpPercent}%` }}></div>
                            </div>
                        </div>
                        <div className="text-gray-400">
                            <span className="text-yellow-400">⚔️ Lv.{stats.level}</span>
                            <span className="ml-2">EXP: {stats.exp}</span>
                        </div>
                    </div>
                </div>

                {/* Chat Area - Messages rendered as separate bubbles */}
                <div className="flex-1 overflow-y-auto mb-4 space-y-3 pr-2">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`p-3 rounded-lg max-w-[85%] ${msg.role === 'user'
                                    ? 'bg-indigo-900 text-white ml-auto'
                                    : msg.role === 'system'
                                        ? 'bg-yellow-900/50 text-yellow-200 text-center w-full font-bold'
                                        : 'bg-gray-800 text-gray-200'
                                }`}
                        >
                            {msg.role === 'user' && <span className="text-indigo-300 text-xs block mb-1">You</span>}
                            {msg.role === 'assistant' && <span className="text-purple-400 text-xs block mb-1">🎭 Dungeon Master</span>}
                            {msg.content}
                        </div>
                    ))}
                    {loading && (
                        <div className="text-gray-500 italic text-sm animate-pulse">The Dungeon Master is thinking...</div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Choice Buttons */}
                {choices.length > 0 && !loading && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                        {choices.map((choice, index) => {
                            const styles = [
                                "bg-emerald-800 hover:bg-emerald-700 border-emerald-600 text-emerald-100",
                                "bg-slate-700 hover:bg-slate-600 border-slate-500 text-slate-200",
                                "bg-rose-900 hover:bg-rose-800 border-rose-700 text-rose-100"
                            ];
                            return (
                                <button
                                    key={index}
                                    onClick={() => handleChoiceClick(choice)}
                                    className={`${styles[index] || styles[0]} border p-3 rounded-lg text-sm font-medium transition-all text-left shadow-lg active:scale-95`}
                                >
                                    {choice}
                                </button>
                            );
                        })}
                    </div>
                )}

                {/* Input Area */}
                <form onSubmit={handleSend} className="flex gap-3">
                    <button
                        type="button"
                        onClick={handleUndo}
                        disabled={loading}
                        className="bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
                        title="Undo"
                    >
                        ↺
                    </button>
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="What do you want to do?"
                        className="flex-1 bg-gray-900 text-white border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-indigo-500"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !sessionId}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors disabled:opacity-50"
                    >
                        Send
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Homepage;
