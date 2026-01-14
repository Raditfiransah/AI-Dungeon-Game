import React from 'react';

const RuneDivider = ({ symbol = '⚔' }) => {
    return (
        <div className="rune-divider">
            <span className="rune">{symbol}</span>
        </div>
    );
};

export default RuneDivider;
