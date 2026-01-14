import React from 'react';

const SectionTitle = ({ children, subtitle, className = '' }) => {
    return (
        <div className={`text-center mb-12 ${className}`}>
            <h2 className="section-title">{children}</h2>
            {subtitle && (
                <p className="text-gray-400 mt-4 max-w-2xl mx-auto text-lg">
                    {subtitle}
                </p>
            )}
        </div>
    );
};

export default SectionTitle;
