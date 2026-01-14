import React from 'react';
import MedievalButton from '../ui/MedievalButton';
import SectionTitle from '../ui/SectionTitle';
import GameCard from '../ui/GameCard';
import RuneDivider from '../ui/RuneDivider';

const LandingPage = () => {
    const featuredGames = [
        {
            title: "The Dark Dungeon",
            description: "Descend into the abyss where ancient evils await. Every choice could be your last in this dark fantasy adventure.",
            difficulty: "Hard",
            genre: "Dark Fantasy",
            slug: "/play"
        },
        {
            title: "Kingdom's Fall",
            description: "The kingdom crumbles as darkness spreads. Rally the remaining knights and save what's left of the realm.",
            difficulty: "Medium",
            genre: "Adventure",
            slug: "/play"
        },
        {
            title: "The Wanderer's Path",
            description: "A mysterious journey through enchanted forests and forgotten ruins. Discover secrets of the old world.",
            difficulty: "Easy",
            genre: "Exploration",
            slug: "/play"
        }
    ];

    return (
        <div className="min-h-screen">
            {/* Hero Section */}
            <section className="relative min-h-[90vh] flex items-center justify-center overflow-hidden">
                {/* Background Gradient */}
                <div className="absolute inset-0 bg-gradient-to-b from-[#0a0f1a] via-[#0f172a] to-[#1e293b]" />

                {/* Decorative Elements */}
                <div className="absolute inset-0 opacity-20">
                    <div className="absolute top-20 left-20 w-64 h-64 bg-[#facc15] rounded-full blur-[120px]" />
                    <div className="absolute bottom-20 right-20 w-96 h-96 bg-[#7f1d1d] rounded-full blur-[150px]" />
                </div>

                {/* Content */}
                <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
                    <h1 className="text-5xl md:text-7xl lg:text-8xl mb-6" style={{ fontFamily: 'var(--font-display)' }}>
                        <span className="bg-gradient-to-r from-[#facc15] via-[#f5f0e1] to-[#facc15] bg-clip-text text-transparent">
                            Enter the Realm
                        </span>
                    </h1>

                    <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-2xl mx-auto leading-relaxed">
                        Where every choice shapes your destiny
                    </p>

                    <p className="text-lg text-gray-400 mb-10 max-w-xl mx-auto">
                        Embark on AI-powered adventures in a world of dark fantasy.
                        Your words are your weapons, your decisions forge your fate.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <MedievalButton to="/play" className="text-lg px-10 py-4">
                            ⚔ Play Now
                        </MedievalButton>
                        <MedievalButton to="/game" variant="outline" className="text-lg px-10 py-4">
                            Explore Games
                        </MedievalButton>
                    </div>

                    {/* Scroll Indicator */}
                    <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
                        <svg className="w-6 h-6 text-[#facc15]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                        </svg>
                    </div>
                </div>
            </section>

            <RuneDivider symbol="⚔" />

            {/* Featured Games Section */}
            <section className="py-20 px-6">
                <div className="max-w-6xl mx-auto">
                    <SectionTitle subtitle="Choose your adventure from our curated collection of AI-powered quests">
                        Featured Quests
                    </SectionTitle>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-12">
                        {featuredGames.map((game, index) => (
                            <GameCard key={index} {...game} />
                        ))}
                    </div>
                </div>
            </section>

            <RuneDivider symbol="🏰" />

            {/* Lore Preview Section */}
            <section className="py-20 px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <SectionTitle subtitle="The ancient scrolls speak of a world where reality bends to imagination">
                        The World Awaits
                    </SectionTitle>

                    <div className="card-medieval mt-8 text-left">
                        <p className="text-gray-300 text-lg leading-relaxed mb-6">
                            In the age of forgotten kingdoms, where magic still flows through ancient ley lines
                            and dragons slumber beneath mountain roots, a new kind of hero emerges. Not bound
                            by the scripts of old tales, but forged through choices made in the crucible of adventure.
                        </p>
                        <p className="text-gray-400 leading-relaxed">
                            The AI Dungeon realm is a living, breathing world that responds to your every word.
                            Whether you seek glory in battle, wisdom in ancient libraries, or fortune in forgotten
                            ruins – the path you walk is yours alone to tread.
                        </p>
                    </div>

                    <MedievalButton to="/about" variant="outline" className="mt-8">
                        Discover the Lore
                    </MedievalButton>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 border-t border-[#facc15]/20">
                <div className="max-w-6xl mx-auto px-6 text-center">
                    <p className="text-gray-500 text-sm">
                        © 2026 AI Dungeon. Forged with ⚔ in the Modern Medieval Realm.
                    </p>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
