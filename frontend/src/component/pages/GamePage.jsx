import React, { useState } from 'react';
import SectionTitle from '../ui/SectionTitle';
import GameCard from '../ui/GameCard';
import RuneDivider from '../ui/RuneDivider';

const GamePage = () => {
    const [filter, setFilter] = useState('all');

    const games = [
        {
            title: "The Dark Dungeon",
            description: "Descend into the abyss where ancient evils await. Every choice could be your last.",
            difficulty: "Hard",
            genre: "Dark Fantasy",
            slug: "/play"
        },
        {
            title: "Kingdom's Fall",
            description: "The kingdom crumbles as darkness spreads. Rally the remaining knights.",
            difficulty: "Medium",
            genre: "Adventure",
            slug: "/play"
        },
        {
            title: "The Wanderer's Path",
            description: "A mysterious journey through enchanted forests and forgotten ruins.",
            difficulty: "Easy",
            genre: "Exploration",
            slug: "/play"
        },
        {
            title: "Dragon's Lair",
            description: "Face the ancient wyrm in its volcanic fortress. Fortune favors the bold.",
            difficulty: "Hard",
            genre: "Action",
            slug: "/play"
        },
        {
            title: "The Cursed Village",
            description: "Something stirs in the mist. Uncover the dark secret haunting Ravenmoor.",
            difficulty: "Medium",
            genre: "Horror",
            slug: "/play"
        },
        {
            title: "Merchant's Fortune",
            description: "Build your trading empire across the realm. Gold is power.",
            difficulty: "Easy",
            genre: "Strategy",
            slug: "/play"
        }
    ];

    const filters = ['all', 'Easy', 'Medium', 'Hard'];

    const filteredGames = filter === 'all'
        ? games
        : games.filter(game => game.difficulty === filter);

    return (
        <div className="min-h-screen py-12 px-6">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <SectionTitle subtitle="Choose your adventure and forge your legend">
                    Quest Archive
                </SectionTitle>

                {/* Filters */}
                <div className="flex flex-wrap justify-center gap-3 mb-12">
                    {filters.map((filterOption) => (
                        <button
                            key={filterOption}
                            onClick={() => setFilter(filterOption)}
                            className={`px-6 py-2 rounded-lg font-semibold transition-all duration-300 capitalize ${filter === filterOption
                                    ? 'bg-[#facc15] text-[#0f172a]'
                                    : 'bg-[#1e293b] text-gray-300 border border-[#facc15]/20 hover:border-[#facc15]/50'
                                }`}
                            style={{ fontFamily: 'var(--font-display)' }}
                        >
                            {filterOption === 'all' ? 'All Quests' : filterOption}
                        </button>
                    ))}
                </div>

                <RuneDivider symbol="📜" />

                {/* Games Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-12">
                    {filteredGames.map((game, index) => (
                        <GameCard key={index} {...game} />
                    ))}
                </div>

                {filteredGames.length === 0 && (
                    <div className="text-center py-20">
                        <p className="text-gray-400 text-xl">No quests found for this difficulty.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GamePage;
