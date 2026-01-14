import React from 'react';
import { Link } from 'react-router-dom';

const MedievalButton = ({ children, variant = 'primary', to, onClick, className = '', ...props }) => {
    const baseClass = variant === 'outline' ? 'btn-medieval-outline' : 'btn-medieval';

    if (to) {
        return (
            <Link to={to} className={`${baseClass} inline-block text-center ${className}`} {...props}>
                {children}
            </Link>
        );
    }

    return (
        <button onClick={onClick} className={`${baseClass} ${className}`} {...props}>
            {children}
        </button>
    );
};

export default MedievalButton;
