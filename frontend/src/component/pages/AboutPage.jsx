import React from 'react';
import SectionTitle from '../ui/SectionTitle';
import MedievalButton from '../ui/MedievalButton';
import RuneDivider from '../ui/RuneDivider';

const AboutPage = () => {
    const creators = [
        { name: "The Architect", role: "Game Design", icon: "🏰" },
        { name: "The Scribe", role: "AI Development", icon: "📜" },
        { name: "The Artisan", role: "Frontend Design", icon: "⚒️" },
        { name: "The Keeper", role: "Backend Systems", icon: "🔮" }
    ];

    return (
        <div className="min-h-screen py-12 px-6">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <SectionTitle subtitle="The tale of how AI Dungeon came to be">
                    Chronicles of the Realm
                </SectionTitle>

                <RuneDivider symbol="📖" />

                {/* Lore Section */}
                <section className="mb-16">
                    <h3 className="text-2xl mb-6 text-[#facc15]" style={{ fontFamily: 'var(--font-display)' }}>
                        The Legend
                    </h3>
                    <div className="card-medieval space-y-6">
                        <p className="text-gray-300 leading-relaxed text-lg">
                            In an age where the boundaries between worlds grew thin, a group of seekers
                            discovered an ancient artifact—a crystal that could channel the whispers of
                            countless souls across infinite timelines. They called it the <span className="text-[#facc15]">Nexus of Narratives</span>.
                        </p>
                        <p className="text-gray-300 leading-relaxed">
                            Using forgotten arts and modern alchemy, they bound this power into a form
                            that any traveler could access. Thus was born the AI Dungeon—a gateway to
                            adventures limited only by imagination itself.
                        </p>
                        <p className="text-gray-400 leading-relaxed">
                            Every quest you undertake adds to the collective memory of the Nexus.
                            Your choices echo through the crystal, inspiring future heroes and
                            shaping stories yet to be told.
                        </p>
                    </div>
                </section>

                <RuneDivider symbol="⚔" />

                {/* Vision Section */}
                <section className="mb-16">
                    <h3 className="text-2xl mb-6 text-[#facc15]" style={{ fontFamily: 'var(--font-display)' }}>
                        Our Vision
                    </h3>
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="card-medieval">
                            <div className="text-3xl mb-4">🎭</div>
                            <h4 className="text-xl text-[#f5f0e1] mb-2" style={{ fontFamily: 'var(--font-display)' }}>
                                Infinite Stories
                            </h4>
                            <p className="text-gray-400">
                                Every adventure is unique. No two journeys through the realm
                                are ever the same.
                            </p>
                        </div>
                        <div className="card-medieval">
                            <div className="text-3xl mb-4">⚔️</div>
                            <h4 className="text-xl text-[#f5f0e1] mb-2" style={{ fontFamily: 'var(--font-display)' }}>
                                Your Choices Matter
                            </h4>
                            <p className="text-gray-400">
                                The world reacts to your decisions. Be the hero, the villain,
                                or forge your own path.
                            </p>
                        </div>
                        <div className="card-medieval">
                            <div className="text-3xl mb-4">🏰</div>
                            <h4 className="text-xl text-[#f5f0e1] mb-2" style={{ fontFamily: 'var(--font-display)' }}>
                                Living World
                            </h4>
                            <p className="text-gray-400">
                                NPCs remember you, kingdoms rise and fall, and legends
                                are written in real-time.
                            </p>
                        </div>
                        <div className="card-medieval">
                            <div className="text-3xl mb-4">🔮</div>
                            <h4 className="text-xl text-[#f5f0e1] mb-2" style={{ fontFamily: 'var(--font-display)' }}>
                                AI Dungeon Master
                            </h4>
                            <p className="text-gray-400">
                                Powered by cutting-edge AI that adapts to your playstyle
                                and keeps the adventure fresh.
                            </p>
                        </div>
                    </div>
                </section>

                <RuneDivider symbol="👑" />

                {/* Creators Section */}
                <section className="mb-16">
                    <h3 className="text-2xl mb-6 text-[#facc15] text-center" style={{ fontFamily: 'var(--font-display)' }}>
                        The Kingdom Creators
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        {creators.map((creator, index) => (
                            <div key={index} className="card-medieval text-center">
                                <div className="text-4xl mb-3">{creator.icon}</div>
                                <h4 className="text-[#f5f0e1] font-semibold" style={{ fontFamily: 'var(--font-display)' }}>
                                    {creator.name}
                                </h4>
                                <p className="text-gray-500 text-sm">{creator.role}</p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* CTA */}
                <div className="text-center">
                    <MedievalButton to="/play" className="text-lg px-10 py-4">
                        Begin Your Journey
                    </MedievalButton>
                </div>
            </div>
        </div>
    );
};

export default AboutPage;
