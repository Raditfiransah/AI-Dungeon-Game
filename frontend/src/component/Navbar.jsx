import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    const navLinks = [
        { path: '/', label: 'Home' },
        { path: '/game', label: 'Games' },
        { path: '/about', label: 'About' },
    ];

    return (
        <nav className="sticky top-0 z-50 flex justify-between items-center bg-[#0a0f1a]/95 backdrop-blur-md text-white h-20 px-6 md:px-16 w-full border-b border-[#facc15]/10">
            <div className="flex items-center gap-8">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-3 group">
                    <span className="text-2xl">⚔</span>
                    <span
                        className="font-bold text-xl tracking-wider text-[#f5f0e1] group-hover:text-[#facc15] transition-colors"
                        style={{ fontFamily: 'var(--font-display)' }}
                    >
                        AI Dungeon
                    </span>
                </Link>

                {/* Nav Links */}
                <ul className="hidden md:flex gap-6 list-none m-0 p-0 text-sm font-medium">
                    {navLinks.map((link) => (
                        <li key={link.path}>
                            <Link
                                to={link.path}
                                className={`relative py-2 transition-colors ${isActive(link.path)
                                        ? 'text-[#facc15]'
                                        : 'text-gray-300 hover:text-[#facc15]'
                                    }`}
                            >
                                {link.label}
                                {isActive(link.path) && (
                                    <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#facc15] rounded-full" />
                                )}
                            </Link>
                        </li>
                    ))}
                </ul>
            </div>

            {/* CTA Button */}
            <div className="flex items-center gap-4">
                <Link
                    to="/play"
                    className="btn-medieval text-sm px-6 py-2"
                >
                    ⚔ Play Now
                </Link>
            </div>
        </nav>
    );
};

export default Navbar;
