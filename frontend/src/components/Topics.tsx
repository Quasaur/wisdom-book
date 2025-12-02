import React, { useState, useEffect } from 'react';

interface TopicsData {
    title: string;
    subtitle: string;
    content: string;
}

const Topics: React.FC = () => {
    const [data, setData] = useState<TopicsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            console.log("Fetching Topics content...");
            try {
                const response = await fetch('/api/topics/');
                console.log("Response status:", response.status);
                if (!response.ok) {
                    throw new Error('Failed to fetch content');
                }
                const jsonData = await response.json();
                console.log("Data received:", jsonData);
                setData(jsonData);
            } catch (err) {
                console.error("Error fetching Topics content:", err);
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
        <div className="card !p-0 overflow-hidden w-[75%]">
            <div className="text-center mb-4 p-4">
                <h1 className="text-2xl font-bold">{data.title}</h1>
                {data.subtitle && (
                    <h2 className="text-xl mt-2"><em>{data.subtitle}</em></h2>
                )}
            </div>
            <div
                className="p-12 pt-4"
                dangerouslySetInnerHTML={{ __html: data.content }}
            />
        </div>
    );
};

export default Topics;
