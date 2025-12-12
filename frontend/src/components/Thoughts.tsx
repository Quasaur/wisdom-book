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
    level: number;
    title: string;
    description: string;
    parent_id: string | null;
    slug: string;
    is_active: boolean;
    neo4j_id: string;
    tags: string[];
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
    const [selectedLanguage, setSelectedLanguage] = useState('en');

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
                // Handle paginated response from ReadOnlyModelViewSet
                const thoughtsData = data.results || data;
                setThoughts(thoughtsData);
                if (thoughtsData.length > 0) {
                    setSelectedThought(thoughtsData[0]);
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
                <p className="font-bold text-sm text-text-secondary mt-1 mb-0">Select a row to view its Details.</p>
            </div>
            <div className="px-4 pb-4 pt-2">
                <div className="overflow-x-auto border border-blue-300 rounded-lg mb-4">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-accent-bg text-text-secondary border-b-2 border-gray-600 italic">
                                <th className="py-1.5 px-3 font-semibold">Thought Level</th>
                                <th className="py-1.5 px-3 font-semibold">Thought Name</th>
                            </tr>
                        </thead>
                        <tbody>
                            {currentThoughts.map((thought, index) => {
                                const isSelected = selectedThought?.id === thought.id;
                                return (
                                    <tr
                                        key={thought.id}
                                        onClick={() => setSelectedThought(thought)}
                                        className={`cursor-pointer transition-colors duration-200 hover:bg-accent-bg/50 ${isSelected
                                            ? 'bg-accent/10 border-l-4 border-accent text-yellow-400'
                                            : index % 2 === 1 ? 'bg-primary-bg/30' : ''
                                            }`}
                                    >
                                        <td className={`py-1.5 px-3 border-b border-border-color ${isSelected ? 'border-l-0' : ''}`}>{thought.level}</td>
                                        <td className="py-1.5 px-3 border-b border-border-color">{thought.title}</td>
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
                                : 'text-yellow-400 hover:bg-accent-bg'}`}
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
                                : 'text-yellow-400 hover:bg-accent-bg'}`}
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
                            <p className="text-sm">Level: {selectedThought.level}</p>
                        </div>
                        {selectedThought.description && (
                            <div>
                                <h4 className="font-semibold mb-1">Description</h4>
                                <p>{selectedThought.description}</p>
                            </div>
                        )}
                        <div>
                            <h4 className="font-semibold mb-1">Details</h4>
                            <div className="details-table-container">
                                <table className="details-table">
                                    <tbody>
                                        <tr className="details-row-odd">
                                            <td className="details-cell-label w-1/2">
                                                <span className="details-label-text">ID:</span> {selectedThought.id}
                                            </td>
                                            <td className="details-cell-value w-1/2">
                                                <span className="details-label-text">Neo4j ID:</span> {selectedThought.neo4j_id}
                                            </td>
                                        </tr>
                                        <tr className="details-row-even">
                                            <td className="details-cell-label">
                                                <span className="details-label-text">Slug:</span> {selectedThought.slug}
                                            </td>
                                            <td className="details-cell-value">
                                                <span className="details-label-text">Status:</span> {selectedThought.is_active ? 'Active' : 'Inactive'}
                                            </td>
                                        </tr>
                                        {selectedThought.parent_id && (
                                            <tr className="details-row-odd">
                                                <td className="details-cell-label">
                                                    <span className="details-label-text">Parent:</span> {selectedThought.parent_id}
                                                </td>
                                                <td className="details-cell-value"></td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        {selectedThought.tags && selectedThought.tags.length > 0 && (
                            <div>
                                <h4 className="tags-section-header">Tags</h4>
                                <div className="tags-container">
                                    {selectedThought.tags.map((tag, index) => (
                                        <span
                                            key={index}
                                            className="tag-pill"
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Content Section with Language Dropdown */}
                        {selectedThought.contents && selectedThought.contents.length > 0 && (
                            <div className="mt-6">
                                <h4 className="content-section-header mb-2">Content</h4>
                                <div className="border border-blue-300 rounded-lg p-4 space-y-4 relative">
                                    <div className="flex justify-end mb-2">
                                        <select
                                            value={selectedLanguage}
                                            onChange={(e) => setSelectedLanguage(e.target.value)}
                                            className="bg-gray-800 border border-yellow-400 text-gray-200 text-sm rounded px-3 py-1 focus:outline-none focus:border-accent cursor-pointer"
                                        >
                                            <option value="en">English</option>
                                            <option value="es">Spanish</option>
                                            <option value="fr">French</option>
                                            <option value="hi">Hindi</option>
                                            <option value="zh">Chinese</option>
                                        </select>
                                    </div>

                                    {/* Link local variables for cleaner render logic */}
                                    {(() => {
                                        const contentObj = selectedThought.contents[0];
                                        let title = contentObj.en_title;
                                        let content = contentObj.en_content;

                                        switch (selectedLanguage) {
                                            case 'es':
                                                title = contentObj.es_title;
                                                content = contentObj.es_content;
                                                break;
                                            case 'fr':
                                                title = contentObj.fr_title;
                                                content = contentObj.fr_content;
                                                break;
                                            case 'hi':
                                                title = contentObj.hi_title;
                                                content = contentObj.hi_content;
                                                break;
                                            case 'zh':
                                                title = contentObj.zh_title;
                                                content = contentObj.zh_content;
                                                break;
                                            default:
                                                title = contentObj.en_title;
                                                content = contentObj.en_content;
                                        }

                                        return (
                                            <>
                                                <div className="bg-primary-bg/40 p-3 rounded-lg border border-blue-500/30 shadow-sm relative group hover:border-blue-400/50 transition-colors">
                                                    <span className="absolute top-0 right-0 px-2 py-0.5 text-[10px] text-blue-300 bg-blue-900/40 rounded-bl rounded-tr uppercase tracking-wider">Title</span>
                                                    <div className="text-gray-100 font-medium text-lg pr-4 pt-1">
                                                        {title || <span className="text-gray-500 italic text-sm">No title available</span>}
                                                    </div>
                                                </div>

                                                <div className="bg-primary-bg/40 p-4 rounded-lg border border-blue-500/30 shadow-sm relative group hover:border-blue-400/50 transition-colors min-h-[100px]">
                                                    <span className="absolute top-0 right-0 px-2 py-0.5 text-[10px] text-blue-300 bg-blue-900/40 rounded-bl rounded-tr uppercase tracking-wider">Content</span>
                                                    <div className="text-gray-300 text-sm leading-normal pt-1">
                                                        {content || <span className="text-gray-500 italic text-sm">No content available</span>}
                                                    </div>
                                                </div>
                                            </>
                                        );
                                    })()}
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
                <div className="w-full max-w-md relative">
                    <input
                        type="text"
                        placeholder="Search thoughts..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full px-4 py-2 pr-10 rounded-lg bg-gray-800 border border-yellow-400 text-gray-200 focus:outline-none focus:border-accent transition-colors duration-200 placeholder-gray-500"
                    />
                    {searchQuery && (
                        <button
                            onClick={() => setSearchQuery('')}
                            className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white focus:outline-none"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    )}
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
