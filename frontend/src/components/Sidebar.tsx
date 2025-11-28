import React, { useState } from 'react';
import './Sidebar.css';

const Sidebar: React.FC = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    };

    return (
        <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`} id="sidebar">
            <div className="sidebar-header">
                <button className="menu-button" onClick={toggleSidebar} aria-label="Toggle Menu">
                    <svg width="24" height="24" viewBox="0 0 24 24">
                        <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" />
                    </svg>
                </button>
                <span className="logo-text">Wisdom Book</span>
            </div>

            <nav className="nav-items">
                <a href="#" className="nav-item active">
                    <div className="nav-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
                        </svg>
                    </div>
                    <span className="nav-label">Start Here!</span>
                </a>
                <a href="#" className="nav-item">
                    <div className="nav-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z" />
                        </svg>
                    </div>
                    <span className="nav-label">Graph View</span>
                </a>
                <a href="#" className="nav-item">
                    <div className="nav-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z" />
                        </svg>
                    </div>
                    <span className="nav-label">Topics</span>
                </a>
                <a href="#" className="nav-item">
                    <div className="nav-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M21.99 4c0-1.1-.89-2-1.99-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4-.01-18z" />
                        </svg>
                    </div>
                    <span className="nav-label">Thoughts</span>
                </a>
                <a href="#" className="nav-item">
                    <div className="nav-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M6 17h3l2-4V7H5v6h3zm8 0h3l2-4V7h-6v6h3z" />
                        </svg>
                    </div>
                    <span className="nav-label">Quotes</span>
                </a>
                <a href="#" className="nav-item">
                    <div className="nav-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z" />
                        </svg>
                    </div>
                    <span className="nav-label">Bible</span>
                </a>
                <a href="#" className="nav-item">
                    <div className="nav-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z" />
                        </svg>
                    </div>
                    <span className="nav-label">Tags</span>
                </a>
                <a href="#" className="nav-item">
                    <div className="nav-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24">
                            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                        </svg>
                    </div>
                    <span className="nav-label">Donate</span>
                </a>
            </nav>
        </div>
    );
};

export default Sidebar;
