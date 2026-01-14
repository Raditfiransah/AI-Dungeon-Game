import React from 'react';
import { Link } from 'react-router-dom';

const GameCard = ({ title, description, image, difficulty, genre, slug = '/play' }) => {
    const difficultyColors = {
        Easy: 'text-emerald-400 bg-emerald-900/30',
        Medium: 'text-yellow-400 bg-yellow-900/30',
        Hard: 'text-red-400 bg-red-900/30',
    };

    return (
        <Link to={slug} className="block">
            <div className="card-medieval group cursor-pointer overflow-hidden">
                {/* Image */}
                <div className="relative h-48 -mx-6 -mt-6 mb-4 overflow-hidden">
                    <div
                        className="w-full h-full bg-cover bg-center transition-transform duration-500 group-hover:scale-110"
                        style={{
                            backgroundImage: image ? `url(${image})` : 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)'
                        }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0f172a] to-transparent" />

                    {/* Badges */}
                    <div className="absolute bottom-3 left-3 flex gap-2">
                        {difficulty && (
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${difficultyColors[difficulty] || difficultyColors.Medium}`}>
                                {difficulty}
                            </span>
                        )}
                        {genre && (
                            <span className="px-2 py-1 rounded text-xs font-semibold bg-slate-700/80 text-slate-200">
                                {genre}
                            </span>
                        )}
                    </div>
                </div>

                {/* Content */}
                <h3
                    className="text-xl font-semibold text-[#f5f0e1] mb-2 group-hover:text-[#facc15] transition-colors"
                    style={{ fontFamily: 'var(--font-display)' }}
                >
                    {title}
                </h3>
                <p className="text-gray-400 text-sm line-clamp-2">
                    {description}
                </p>

                {/* Play Button */}
                <div className="mt-4 flex items-center text-[#facc15] text-sm font-semibold">
                    <span>Play Now</span>
                    <svg className="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        </Link>
    );
};

export default GameCard;
