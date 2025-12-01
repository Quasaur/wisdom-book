import React, { useState, useEffect, useRef } from 'react';

interface StartHereData {
    title: string;
    subtitle: string;
    hero_image_url: string;
    content: string;
}

interface TOCItem {
    id: string;
    text: string;
}

const StartHere: React.FC = () => {
    const [data, setData] = useState<StartHereData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [toc, setToc] = useState<TOCItem[]>([]);
    const contentRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const fetchData = async () => {
            console.log("Fetching Start Here content...");
            try {
                const response = await fetch('http://localhost:8000/api/start-here/');
                console.log("Response status:", response.status);
                if (!response.ok) {
                    throw new Error('Failed to fetch content');
                }
                const jsonData = await response.json();
                console.log("Data received:", jsonData);
                setData(jsonData);
            } catch (err) {
                console.error("Error fetching Start Here content:", err);
                setError("Failed to load content. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Generate TOC and assign IDs to headings
    useEffect(() => {
        if (data && contentRef.current) {
            const headings = contentRef.current.querySelectorAll('h2');
            // Initialize TOC with the Welcome heading
            const newToc: TOCItem[] = [
                { id: 'start-here-card', text: data.title }
            ];

            headings.forEach((heading, index) => {
                const text = heading.textContent || `Section ${index + 1}`;
                const id = text
                    .toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/(^-|-$)/g, '');

                heading.id = id;
                newToc.push({ id, text });
            });

            setToc(newToc);
        }
    }, [data]);

    if (loading) {
        return (
            <div className="card !p-0 overflow-hidden min-h-[400px] flex items-center justify-center">
                <div className="text-text-secondary">Loading content...</div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="card !p-0 overflow-hidden min-h-[400px] flex items-center justify-center">
                <div className="text-red-400">{error || "No content available"}</div>
            </div>
        );
    }

    const SH_Card_01 = (
        <div id="start-here-card" className="card !p-0 overflow-hidden w-[75%]">
            <div className="text-center mb-4 p-4">
                <h1 className="text-2xl font-bold">{data.title}</h1>
                {data.subtitle && (
                    <h2 className="text-xl mt-2"><em>{data.subtitle}</em></h2>
                )}
            </div>
            {data.hero_image_url && (
                <img
                    src={data.hero_image_url}
                    alt="Start Here Hero"
                    className="w-[40%] h-auto mx-auto block mt-[5px]"
                />
            )}
            <div
                ref={contentRef}
                className="p-12 pt-4"
                dangerouslySetInnerHTML={{ __html: data.content }}
            />
        </div>
    );

    const SH_Card_02 = (
        <div className="card flex-1 h-fit sticky top-0">
            <h3 className="text-lg font-bold mb-4 text-text-primary border-b border-border-color pb-2">
                Table of Contents
            </h3>
            <nav className="flex flex-col gap-2">
                {toc.map((item) => (
                    <a
                        key={item.id}
                        href={`#${item.id}`}
                        className="text-xs text-text-secondary hover:text-accent whitespace-nowrap overflow-hidden text-ellipsis transition-colors duration-200"
                        title={item.text}
                    >
                        {item.text}
                    </a>
                ))}
            </nav>
        </div>
    );

    return (
        <div className="flex gap-[60px] items-start">
            {SH_Card_01}
            {SH_Card_02}
        </div>
    );
};

export default StartHere;
