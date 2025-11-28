import React from 'react';
import Sidebar from './Sidebar';

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                <header className="h-header-height bg-primary-bg flex items-center justify-between px-6 border-b border-border-color">
                    <div className="text-3xl font-bold text-yellow-400">Start Here!</div>
                    <div className="flex gap-4">
                        <svg width="24" height="24" viewBox="0 0 24 24" className="text-text-secondary cursor-pointer fill-current">
                            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
                        </svg>
                    </div>
                </header>
                <main className="flex-1 overflow-y-auto p-16 w-full box-border bg-content-bg">
                    {children}
                </main>
                <footer className="py-4 px-6 text-center text-text-secondary text-sm border-t border-border-color">
                    &copy; 2025 Quasaur. Wisdom is Priceless.
                </footer>
            </div>
        </div>
    );
};

export default Layout;
