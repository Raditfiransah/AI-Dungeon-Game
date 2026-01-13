import React from 'react';

const Navbar = () => {
    return (
        <nav className="flex justify-between items-center bg-[#1D1616] text-white h-24 px-16 w-full shadow-md">
            <div className="flex items-center gap-8">
                <div className="font-bold text-2xl tracking-wider">AI Dungeon</div>
                <ul className="flex gap-8 list-none m-0 p-0 text-sm font-medium">
                    <li className="cursor-pointer hover:text-gray-300 transition-colors">Home</li>
                    <li className="cursor-pointer hover:text-gray-300 transition-colors">Game</li>
                    <li className="cursor-pointer hover:text-gray-300 transition-colors">About</li>
                </ul>
            </div>
            <div className="flex items-center">
                <button className="bg-white text-black px-5 py-2 rounded-full hover:bg-gray-100 transition-colors font-semibold text-sm">
                    Play Now        
                </button>
            </div>
        </nav>
    );
};

export default Navbar;
