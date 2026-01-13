import React, { useState, useEffect, useRef } from 'react';

const Homepage = () => {
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
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
        startNewGame();
    }, []);

    const startNewGame = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/game/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ starting_scenario: "You stand at the entrance of a dark, ominous dungeon." }),
            });
            const data = await response.json();
            setSessionId(data.session_id);
            setMessages([{ type: 'assistant', text: data.history }]);
        } catch (error) {
            console.error('Error starting game:', error);
            setMessages([{ type: 'error', text: "Failed to connect to the dungeon master (Backend)." }]);
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || !sessionId || loading) return;

        const userMessage = input;
        setInput('');
        setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/game/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    action: userMessage
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Action failed');
            }

            const data = await response.json();
            setMessages(prev => [...prev, { type: 'assistant', text: data.narrative }]);

            if (data.game_over) {
                setMessages(prev => [...prev, { type: 'system', text: "GAME OVER" }]);
            }

        } catch (error) {
            console.error('Error sending action:', error);
            setMessages(prev => [...prev, { type: 'error', text: "Something went wrong. Try again." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex justify-center items-start min-h-[calc(100vh-6rem)] pt-10 px-4">
            <div className="bg-[#1a1a1a] p-6 rounded-xl shadow-2xl w-full max-w-3xl border border-gray-800 flex flex-col h-[600px]">

                {/* Header */}
                <div className="mb-4 border-b border-gray-700 pb-4">
                    <h2 className="text-2xl font-bold text-white mb-1">Dungeon Log</h2>
                    <p className="text-gray-400 text-sm">Adventure awaits via localhost:8000</p>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`p-3 rounded-lg max-w-[85%] ${msg.type === 'user'
                                    ? 'bg-indigo-900 text-white self-end ml-auto'
                                    : msg.type === 'error'
                                        ? 'bg-red-900/50 text-red-200'
                                        : msg.type === 'system'
                                            ? 'bg-yellow-900/50 text-yellow-200 text-center w-full font-bold'
                                            : 'bg-gray-800 text-gray-200'
                                }`}
                        >
                            {msg.text}
                        </div>
                    ))}
                    {loading && (
                        <div className="text-gray-500 italic text-sm animate-pulse">The Dungeon Master is thinking...</div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <form onSubmit={handleSend} className="flex gap-3 mt-auto">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="What do you want to do?"
                        className="flex-1 bg-gray-900 text-white border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:border-indigo-500 transition-colors"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !sessionId}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Send
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Homepage;
