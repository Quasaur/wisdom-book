import React, { useState, useEffect } from 'react';

interface Content {
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

interface Thought {
    id: number;
    title: string;
    description: string;
    parent_id: string | null;
    slug: string;
    is_active: boolean;
    neo4j_id: string;
    contents: Content[];
}

const Thoughts: React.FC = () => {
    const [thoughts, setThoughts] = useState<Thought[]>([]);
    const [selectedThought, setSelectedThought] = useState<Thought | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [searchQuery, setSearchQuery] = useState('');
    const itemsPerPage = 10;

    useEffect(() => {
        const fetchThoughts = async () => {
            console.log("Fetching Thoughts...");
            try {
                const response = await fetch('/api/thoughts/');
                console.log("Response status:", response.status);
                if (!response.ok) {
                    throw new Error('Failed to fetch thoughts');
                }
                const data = await response.json();
                console.log("Data received:", data);
                setThoughts(data);
                if (data.length > 0) {
                    setSelectedThought(data[0]);
                }
            } catch (err) {
                console.error("Error fetching Thoughts:", err);
                setError("Failed to load thoughts. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        fetchThoughts();
    }, []);

    // Filter thoughts based on search query
    const filteredThoughts = thoughts.filter(thought =>
        thought.title.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Calculate pagination
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentThoughts = filteredThoughts.slice(indexOfFirstItem, indexOfLastItem);
    const totalPages = Math.ceil(filteredThoughts.length / itemsPerPage);

    const paginate = (pageNumber: number) => setCurrentPage(pageNumber);

    // Reset pagination when search query changes
    useEffect(() => {
        setCurrentPage(1);
    }, [searchQuery]);

    if (loading) {
        return (
            <div className="card !p-0 overflow-hidden min-h-[400px] flex items-center justify-center">
                <div className="text-text-secondary">Loading thoughts...</div>
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

    const TC_Card_01 = (
        <div className="card !p-0 overflow-hidden flex-1 h-fit">
            <div className="px-4 py-2 border-b border-border-color text-center">
                <h2 className="text-xl font-bold mt-0">Thoughts</h2>
            </div>
            <div className="px-4 pb-4 pt-2">
                <div className="overflow-x-auto border border-blue-300 rounded-lg mb-4">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-bg-secondary text-text-secondary border-b-2 border-gray-600 italic">
                                <th className="p-3 font-semibold">Thought Name</th>
                                <th className="p-3 font-semibold">Parent Topic</th>
                            </tr>
                        </thead>
                        <tbody>
                            {currentThoughts.map((thought, index) => {
                                const isSelected = selectedThought?.id === thought.id;
                                return (
                                    <tr
                                        key={thought.id}
                                        onClick={() => setSelectedThought(thought)}
                                        className={`cursor-pointer transition-colors duration-200 hover:bg-bg-secondary/50 ${isSelected
                                            ? 'bg-accent/10 border-l-4 border-accent text-yellow-400'
                                            : index % 2 === 1 ? 'bg-primary-bg/30' : ''
                                            }`}
                                    >
                                        <td className={`p-3 border-b border-border-color ${isSelected ? 'border-l-0' : ''}`}>{thought.title}</td>
                                        <td className="p-3 border-b border-border-color">{thought.parent_id || '-'}</td>
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

    const TC_Card_02 = (
        <div className="card !p-0 overflow-hidden flex-1 h-fit sticky top-0">
            <div className="px-4 py-2 border-b border-border-color text-center">
                <h2 className="text-xl font-bold mt-0">Selected Thought Detail</h2>
            </div>
            <div className="px-6 pb-6 pt-3">
                {selectedThought ? (
                    <div className="space-y-4 text-gray-300">
                        <div>
                            <h3 className="text-lg font-semibold text-accent">{selectedThought.title}</h3>
                        </div>
                        {selectedThought.description && (
                            <div>
                                <h4 className="font-semibold mb-1">Description</h4>
                                <p>{selectedThought.description}</p>
                            </div>
                        )}
                        <div>
                            <h4 className="font-semibold mb-1">Details</h4>
                            <ul className="list-disc list-inside text-sm space-y-1">
                                <li>ID: {selectedThought.id}</li>
                                <li>Neo4j ID: {selectedThought.neo4j_id}</li>
                                <li>Slug: {selectedThought.slug}</li>
                                <li>Status: {selectedThought.is_active ? 'Active' : 'Inactive'}</li>
                            </ul>
                        </div>

                        {/* Content Table */}
                        {selectedThought.contents && selectedThought.contents.length > 0 && (
                            <div className="mt-6">
                                <h4 className="font-semibold mb-1">Content</h4>
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
                                                { lang: 'English', title: selectedThought.contents[0].en_title, content: selectedThought.contents[0].en_content },
                                                { lang: 'Spanish', title: selectedThought.contents[0].es_title, content: selectedThought.contents[0].es_content },
                                                { lang: 'French', title: selectedThought.contents[0].fr_title, content: selectedThought.contents[0].fr_content },
                                                { lang: 'Hindi', title: selectedThought.contents[0].hi_title, content: selectedThought.contents[0].hi_content },
                                                { lang: 'Chinese', title: selectedThought.contents[0].zh_title, content: selectedThought.contents[0].zh_content },
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
                    <div className="text-text-secondary italic">Select a thought to view details</div>
                )}
            </div>
        </div>
    );

    return (
        <div className="flex flex-col gap-6 -mt-[30px]">
            {/* Search Widget */}
            <div className="flex justify-center">
                <div className="w-full max-w-md">
                    <input
                        type="text"
                        placeholder="Search thoughts..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-yellow-400 text-gray-200 focus:outline-none focus:border-accent transition-colors duration-200 placeholder-gray-500"
                    />
                </div>
            </div>

            <div className="flex gap-[60px] items-start">
                {TC_Card_01}
                {TC_Card_02}
            </div>
        </div>
    );
};

export default Thoughts;
