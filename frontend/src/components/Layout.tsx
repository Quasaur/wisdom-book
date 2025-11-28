import React from 'react';
import Sidebar from './Sidebar';
import './Layout.css';

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className="app-container">
            <Sidebar />
            <div className="main-wrapper">
                <header className="header">
                    <div className="header-title">Welcome to the Book of Thoughts</div>
                    <div style={{ display: 'flex', gap: '16px' }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" style={{ color: 'var(--text-secondary)', cursor: 'pointer' }}>
                            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
                        </svg>
                    </div>
                </header>
                <main className="content-area">
                    {children}
                </main>
                <footer className="footer">
                    &copy; 2025 Quasaur. Wisdom is Priceless.
                </footer>
            </div>
        </div>
    );
};

export default Layout;
