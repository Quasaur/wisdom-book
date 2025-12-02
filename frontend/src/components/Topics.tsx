import React, { useState, useEffect } from 'react';

interface Topic {
    id: number;
    level: number;
    title: string;
    description: string;
    slug: string;
    is_active: boolean;
    neo4j_id: string;
}

const Topics: React.FC = () => {
    const [topics, setTopics] = useState<Topic[]>([]);
    const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchTopics = async () => {
            console.log("Fetching Topics...");
            try {
                const response = await fetch('/api/topics/');
                console.log("Response status:", response.status);
                if (!response.ok) {
                    throw new Error('Failed to fetch topics');
                }
                const data = await response.json();
                console.log("Data received:", data);
                setTopics(data);
                if (data.length > 0) {
                    setSelectedTopic(data[0]);
                }
            } catch (err) {
                console.error("Error fetching Topics:", err);
                setError("Failed to load topics. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        fetchTopics();
    }, []);

    if (loading) {
        return (
            <div className="card !p-0 overflow-hidden min-h-[400px] flex items-center justify-center">
                <div className="text-text-secondary">Loading topics...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card !p-0 overflow-hidden min-h-[400px] flex items-center justify-center">
                <div className="text-red-400">{error}</div>
            </div>
        );
    }

    const T_Card_01 = (
        <div className="card !p-0 overflow-hidden flex-1 h-fit">
            <div className="p-4 border-b border-border-color text-center">
                <h2 className="text-xl font-bold mt-0">Topics</h2>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-bg-secondary text-text-secondary">
                            <th className="p-3 border-b border-border-color font-semibold">Topic Level</th>
                            <th className="p-3 border-b border-border-color font-semibold">Topic Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        {topics.map((topic) => (
                            <tr
                                key={topic.id}
                                onClick={() => setSelectedTopic(topic)}
                                className={`cursor-pointer transition-colors duration-200 hover:bg-bg-secondary/50 ${selectedTopic?.id === topic.id ? 'bg-accent/10 border-l-4 border-accent' : ''
                                    }`}
                            >
                                <td className="p-3 border-b border-border-color">{topic.level}</td>
                                <td className="p-3 border-b border-border-color">{topic.title}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );

    const T_Card_02 = (
        <div className="card !p-0 overflow-hidden flex-1 h-fit sticky top-0">
            <div className="p-4 border-b border-border-color text-center">
                <h2 className="text-xl font-bold mt-0">Selected Topic Detail</h2>
            </div>
            <div className="p-6">
                {selectedTopic ? (
                    <div className="space-y-4">
                        <div>
                            <h3 className="text-lg font-semibold text-accent">{selectedTopic.title}</h3>
                            <p className="text-sm text-text-secondary">Level: {selectedTopic.level}</p>
                        </div>
                        {selectedTopic.description && (
                            <div>
                                <h4 className="font-semibold mb-1">Description</h4>
                                <p className="text-text-primary">{selectedTopic.description}</p>
                            </div>
                        )}
                        <div>
                            <h4 className="font-semibold mb-1">Details</h4>
                            <ul className="list-disc list-inside text-sm text-text-secondary space-y-1">
                                <li>ID: {selectedTopic.id}</li>
                                <li>Neo4j ID: {selectedTopic.neo4j_id}</li>
                                <li>Slug: {selectedTopic.slug}</li>
                                <li>Status: {selectedTopic.is_active ? 'Active' : 'Inactive'}</li>
                            </ul>
                        </div>
                    </div>
                ) : (
                    <div className="text-text-secondary italic">Select a topic to view details</div>
                )}
            </div>
        </div>
    );

    return (
        <div className="flex gap-[60px] items-start">
            {T_Card_01}
            {T_Card_02}
        </div>
    );
};

export default Topics;
