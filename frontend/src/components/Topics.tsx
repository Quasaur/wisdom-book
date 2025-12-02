import React, { useState, useEffect } from 'react';

interface Description {
    en_title: string;
    en_content: string;
    es_title: string;
    es_content: string;
    fr_title: string;
    fr_content: string;
    hi_title: string;
    hi_content: string;
    zh_title: string;
    zh_content: string;
}

interface Topic {
    id: number;
    level: number;
    title: string;
    description: string;
    slug: string;
    is_active: boolean;
    neo4j_id: string;
    tags: string[];
    descriptions: Description[];
}

const Topics: React.FC = () => {
    const [topics, setTopics] = useState<Topic[]>([]);
    const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 10;

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

    // Calculate pagination
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentTopics = topics.slice(indexOfFirstItem, indexOfLastItem);
    const totalPages = Math.ceil(topics.length / itemsPerPage);

    const paginate = (pageNumber: number) => setCurrentPage(pageNumber);

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
            <div className="px-4 py-2 border-b border-border-color text-center">
                <h2 className="text-xl font-bold mt-0">Topics</h2>
            </div>
            <div className="px-4 pb-4 pt-2">
                <div className="overflow-x-auto border border-blue-300 rounded-lg mb-4">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-bg-secondary text-text-secondary border-b-2 border-gray-600 italic">
                                <th className="p-3 font-semibold">Topic Level</th>
                                <th className="p-3 font-semibold">Topic Name</th>
                            </tr>
                        </thead>
                        <tbody>
                            {currentTopics.map((topic, index) => {
                                const isSelected = selectedTopic?.id === topic.id;
                                return (
                                    <tr
                                        key={topic.id}
                                        onClick={() => setSelectedTopic(topic)}
                                        className={`cursor-pointer transition-colors duration-200 hover:bg-bg-secondary/50 ${isSelected
                                            ? 'bg-accent/10 border-l-4 border-accent text-yellow-400'
                                            : index % 2 === 1 ? 'bg-primary-bg/30' : ''
                                            }`}
                                    >
                                        <td className={`p-3 border-b border-border-color ${isSelected ? 'border-l-0' : ''}`}>{topic.level}</td>
                                        <td className="p-3 border-b border-border-color">{topic.title}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>

                {/* Pagination Controls */}
                {totalPages > 1 && (
                    <div className="flex justify-between items-center px-2">
                        <button
                            onClick={() => paginate(Math.max(1, currentPage - 1))}
                            disabled={currentPage === 1}
                            className={`px-3 py-1 rounded text-sm ${currentPage === 1
                                ? 'text-text-secondary opacity-50 cursor-not-allowed'
                                : 'text-yellow-400 hover:bg-bg-secondary'}`}
                        >
                            Previous
                        </button>
                        <span className="text-sm text-text-secondary">
                            Page {currentPage} of {totalPages}
                        </span>
                        <button
                            onClick={() => paginate(Math.min(totalPages, currentPage + 1))}
                            disabled={currentPage === totalPages}
                            className={`px-3 py-1 rounded text-sm ${currentPage === totalPages
                                ? 'text-text-secondary opacity-50 cursor-not-allowed'
                                : 'text-yellow-400 hover:bg-bg-secondary'}`}
                        >
                            Next
                        </button>
                    </div>
                )}
            </div>
        </div>
    );

    const T_Card_02 = (
        <div className="card !p-0 overflow-hidden flex-1 h-fit sticky top-0">
            <div className="px-4 py-2 border-b border-border-color text-center">
                <h2 className="text-xl font-bold mt-0">Selected Topic Detail</h2>
            </div>
            <div className="px-6 pb-6 pt-3">
                {selectedTopic ? (
                    <div className="space-y-4 text-gray-300">
                        <div>
                            <h3 className="text-lg font-semibold text-accent">{selectedTopic.title}</h3>
                            <p className="text-sm">Level: {selectedTopic.level}</p>
                        </div>
                        {selectedTopic.description && (
                            <div>
                                <h4 className="font-semibold mb-1">Description</h4>
                                <p>{selectedTopic.description}</p>
                            </div>
                        )}
                        <div>
                            <h4 className="font-semibold mb-1">Details</h4>
                            <ul className="list-disc list-inside text-sm space-y-1">
                                <li>ID: {selectedTopic.id}</li>
                                <li>Neo4j ID: {selectedTopic.neo4j_id}</li>
                                <li>Slug: {selectedTopic.slug}</li>
                                <li>Status: {selectedTopic.is_active ? 'Active' : 'Inactive'}</li>
                            </ul>
                        </div>
                        {selectedTopic.tags && selectedTopic.tags.length > 0 && (
                            <div>
                                <h4 className="font-semibold mb-2">Tags</h4>
                                <div className="flex flex-wrap gap-2">
                                    {selectedTopic.tags.map((tag, index) => (
                                        <span
                                            key={index}
                                            className="px-2 py-1 bg-bg-secondary text-xs rounded-full border border-border-color"
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Description Table */}
                        {selectedTopic.descriptions && selectedTopic.descriptions.length > 0 && (
                            <div className="mt-6">
                                <h3 className="text-lg font-semibold text-gray-200 mb-2">Description</h3>
                                <div className="overflow-x-auto border border-blue-300 rounded-lg">
                                    <table className="w-full text-left border-collapse">
                                        <thead>
                                            <tr className="bg-bg-secondary text-text-secondary border-b-2 border-gray-600 italic">
                                                <th className="p-3 font-semibold w-24">Language</th>
                                                <th className="p-3 font-semibold w-48">Title</th>
                                                <th className="p-3 font-semibold">Content</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {[
                                                { lang: 'English', title: selectedTopic.descriptions[0].en_title, content: selectedTopic.descriptions[0].en_content },
                                                { lang: 'Spanish', title: selectedTopic.descriptions[0].es_title, content: selectedTopic.descriptions[0].es_content },
                                                { lang: 'French', title: selectedTopic.descriptions[0].fr_title, content: selectedTopic.descriptions[0].fr_content },
                                                { lang: 'Hindi', title: selectedTopic.descriptions[0].hi_title, content: selectedTopic.descriptions[0].hi_content },
                                                { lang: 'Chinese', title: selectedTopic.descriptions[0].zh_title, content: selectedTopic.descriptions[0].zh_content },
                                            ].map((row, index) => (
                                                <tr
                                                    key={index}
                                                    className={`transition-colors duration-200 hover:bg-bg-secondary/50 ${index % 2 === 1 ? 'bg-primary-bg/30' : ''
                                                        }`}
                                                >
                                                    <td className="p-3 border-b border-border-color font-medium">{row.lang}</td>
                                                    <td className="p-3 border-b border-border-color">{row.title}</td>
                                                    <td className="p-3 border-b border-border-color">{row.content}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
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
