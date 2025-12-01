import React, { useState, useEffect } from 'react';

interface StartHereData {
    title: string;
    subtitle: string;
    hero_image_url: string;
    content: string;
}

const StartHere: React.FC = () => {
    const [data, setData] = useState<StartHereData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/start-here/');
                if (!response.ok) {
                    throw new Error('Failed to fetch content');
                }
                const jsonData = await response.json();
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

    return (
        <div className="card !p-0 overflow-hidden">
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
                className="p-12 pt-4"
                dangerouslySetInnerHTML={{ __html: data.content }}
            />
        </div>
    );
};

export default StartHere;
