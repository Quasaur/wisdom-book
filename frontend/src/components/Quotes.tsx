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

interface Quote {
    id: number;
    title: string;
    author: string;
    source: string;
    book_link: string;
    slug: string;
    is_active: boolean;
    neo4j_id: string;
    contents: Content[];
    tags: string[];
}

const Quotes: React.FC = () => {
    const [quotes, setQuotes] = useState<Quote[]>([]);
    const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [searchQuery, setSearchQuery] = useState('');
    const itemsPerPage = 10;

    useEffect(() => {
        const fetchQuotes = async () => {
            console.log("Fetching Quotes...");
            try {
                const response = await fetch('/api/quotes/');
                console.log("Response status:", response.status);
                if (!response.ok) {
                    throw new Error('Failed to fetch quotes');
                }
                const data = await response.json();
                console.log("Data received:", data);
                setQuotes(data);
                if (data.length > 0) {
                    setSelectedQuote(data[0]);
                }
            } catch (err) {
                console.error("Error fetching Quotes:", err);
                setError("Failed to load quotes. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        fetchQuotes();
    }, []);

    // Filter quotes based on search query
    const filteredQuotes = quotes.filter(quote =>
        quote.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        quote.author.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Calculate pagination
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentQuotes = filteredQuotes.slice(indexOfFirstItem, indexOfLastItem);
    const totalPages = Math.ceil(filteredQuotes.length / itemsPerPage);

    const paginate = (pageNumber: number) => setCurrentPage(pageNumber);

    // Reset pagination when search query changes
    useEffect(() => {
        setCurrentPage(1);
    }, [searchQuery]);

    if (loading) {
        return (
            <div className="card !p-0 overflow-hidden min-h-[400px] flex items-center justify-center">
                <div className="text-text-secondary">Loading quotes...</div>
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

    const Q_Card_01 = (
        <div className="card !p-0 overflow-hidden flex-1 h-fit">
            <div className="px-4 py-2 border-b border-border-color text-center">
                <h2 className="text-xl font-bold mt-0">Quotes</h2>
                <p className="font-bold text-sm text-text-secondary mt-1 mb-0">Select a row to view its Details.</p>
            </div>
            <div className="px-4 pb-4 pt-2">
                <div className="overflow-x-auto border border-blue-300 rounded-lg mb-4">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-accent-bg text-text-secondary border-b-2 border-gray-600 italic">
                                <th className="p-3 font-semibold">Quote</th>
                                <th className="p-3 font-semibold">Author</th>
                            </tr>
                        </thead>
                        <tbody>
                            {currentQuotes.map((quote, index) => {
                                const isSelected = selectedQuote?.id === quote.id;
                                return (
                                    <tr
                                        key={quote.id}
                                        onClick={() => setSelectedQuote(quote)}
                                        className={`cursor-pointer transition-colors duration-200 hover:bg-accent-bg/50 ${isSelected
                                            ? 'bg-accent/10 border-l-4 border-accent text-yellow-400'
                                            : index % 2 === 1 ? 'bg-primary-bg/30' : ''
                                            }`}
                                    >
                                        <td className={`p-3 border-b border-border-color ${isSelected ? 'border-l-0' : ''}`}>{quote.title}</td>
                                        <td className="p-3 border-b border-border-color">{quote.author || '-'}</td>
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

    const Q_Card_02 = (
        <div className="card !p-0 overflow-hidden flex-1 h-fit sticky top-0">
            <div className="px-4 py-2 border-b border-border-color text-center">
                <h2 className="text-xl font-bold mt-0">Selected Quote Detail</h2>
            </div>
            <div className="px-6 pb-6 pt-3">
                {selectedQuote ? (
                    <div className="space-y-4 text-gray-300">
                        <div>
                            <h3 className="text-lg font-semibold text-accent">{selectedQuote.title}</h3>
                            {selectedQuote.author && (
                                <p className="text-sm text-text-secondary italic">- {selectedQuote.author}</p>
                            )}
                        </div>

                        <div>
                            <h4 className="font-semibold mb-1">Details</h4>
                            <div className="details-table-container">
                                <table className="details-table">
                                    <tbody>
                                        <tr className="details-row-odd">
                                            <td className="details-cell-label w-1/2">
                                                <span className="details-label-text">ID:</span> {selectedQuote.id}
                                            </td>
                                            <td className="details-cell-value w-1/2">
                                                <span className="details-label-text">Neo4j ID:</span> {selectedQuote.neo4j_id}
                                            </td>
                                        </tr>
                                        <tr className="details-row-even">
                                            <td className="details-cell-label">
                                                <span className="details-label-text">Slug:</span> {selectedQuote.slug}
                                            </td>
                                            <td className="details-cell-value">
                                                <span className="details-label-text">Status:</span> {selectedQuote.is_active ? 'Active' : 'Inactive'}
                                            </td>
                                        </tr>
                                        {selectedQuote.source && (
                                            <tr className="bg-primary-bg/30 border-t border-border-color transition-colors duration-200 hover:bg-accent-bg/50">
                                                <td className="details-cell-label">
                                                    <span className="details-label-text">Source:</span> {selectedQuote.source}
                                                </td>
                                                <td className="details-cell-value">
                                                    {selectedQuote.book_link && (
                                                        <>
                                                            <span className="details-label-text">Book Link:</span> <a href={selectedQuote.book_link} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline break-all">{selectedQuote.book_link}</a>
                                                        </>
                                                    )}
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Tags Section */}
                        {selectedQuote.tags && selectedQuote.tags.length > 0 && (
                            <div>
                                <h4 className="tags-section-header">Tags</h4>
                                <div className="tags-container">
                                    {selectedQuote.tags.map((tag, index) => (
                                        <span key={index} className="tag-pill">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Content Table */}
                        {selectedQuote.contents && selectedQuote.contents.length > 0 && (
                            <div className="mt-6">
                                <h4 className="content-section-header">Content</h4>
                                <div className="content-table-container">
                                    <table className="content-table">
                                        <thead>
                                            <tr className="content-table-head-row">
                                                <th className="content-table-th w-24">Language</th>
                                                <th className="content-table-th w-48">Title</th>
                                                <th className="content-table-th">Content</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {[
                                                { lang: 'English', title: selectedQuote.contents[0].en_title, content: selectedQuote.contents[0].en_content },
                                                { lang: 'Spanish', title: selectedQuote.contents[0].es_title, content: selectedQuote.contents[0].es_content },
                                                { lang: 'French', title: selectedQuote.contents[0].fr_title, content: selectedQuote.contents[0].fr_content },
                                                { lang: 'Hindi', title: selectedQuote.contents[0].hi_title, content: selectedQuote.contents[0].hi_content },
                                                { lang: 'Chinese', title: selectedQuote.contents[0].zh_title, content: selectedQuote.contents[0].zh_content },
                                            ].map((row, index) => (
                                                <tr
                                                    key={index}
                                                    className={index % 2 === 1 ? 'content-table-row-odd' : 'content-table-row-even'}
                                                >
                                                    <td className="content-table-cell font-medium align-top">{row.lang}</td>
                                                    <td className="content-table-cell align-top">{row.title}</td>
                                                    <td className="content-table-cell">{row.content}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="text-text-secondary italic">Select a quote to view details</div>
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
                        placeholder="Search quotes..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-yellow-400 text-gray-200 focus:outline-none focus:border-accent transition-colors duration-200 placeholder-gray-500"
                    />
                </div>
            </div>

            <div className="flex gap-[60px] items-start">
                {Q_Card_01}
                {Q_Card_02}
            </div>
        </div>
    );
};

export default Quotes;
