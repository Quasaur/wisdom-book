import React from 'react';
import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const location = useLocation();

    const getPageTitle = () => {
        let title = '';
        switch (location.pathname) {
            case '/':
                title = 'Start Here!';
                break;
            case '/graph':
                title = 'Graph View';
                break;
            case '/topics':
                title = 'Topics';
                break;
            case '/thoughts':
                title = 'Thoughts';
                break;
            case '/quotes':
                title = 'Quotes';
                break;
            case '/bible':
                title = 'Bible';
                break;
            case '/tags':
                title = 'Tags';
                break;
            case '/donate':
                title = 'Donate';
                break;
            default:
                title = 'Wisdom Book';
        }
        return `${title} | The Book of Wisdom`;
    };

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                <header className="h-header-height bg-primary-bg flex items-center justify-between px-6 border-b border-border-color">
                    <div className="text-3xl font-bold text-yellow-400">{getPageTitle()}</div>
                    <div className="flex gap-4">

                    </div>
                </header>
                <main className="flex-1 overflow-y-auto p-[60px] w-full box-border bg-content-bg">
                    {children}
                </main>
                <footer className="py-4 px-6 text-center text-text-secondary text-sm border-t border-border-color flex flex-col gap-2">
                    {location.pathname === '/graph' && (
                        <div className="text-yellow-400 font-medium">
                            Use <strong>Ctrl + Scroll</strong> to zoom the graph. Click and drag to pan. <br />
                            Press <strong>Alt + R</strong> to reset view.
                        </div>
                    )}
                    <div>&copy; 2025 Calvin Lamont Mitchell. Wisdom is Priceless.</div>
                </footer>
            </div>
        </div>
    );
};

export default Layout;
