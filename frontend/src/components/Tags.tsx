import React, { useState, useEffect } from 'react';
import { Search, Hash, FileText, MessageSquare, Book, LayoutGrid, AlertCircle, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

interface TagSource {
    id: number;
    name: string;
    source_type: string;
    source_id: string;
    tags: string[];
}

interface TagData {
    name: string;
    count: number;
}

interface DetailNode {
    id: number;
    title: string;
    description?: string;
    text?: string;
    content?: string;
    tags?: string[];
    contents?: any[];
    descriptions?: any[];
    [key: string]: any;
}

const Tags: React.FC = () => {
    // State
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedTag, setSelectedTag] = useState<TagData | null>(null);
    const [selectedSource, setSelectedSource] = useState<TagSource | null>(null);
    const [selectedDetailNode, setSelectedDetailNode] = useState<DetailNode | null>(null);
    const [selectedLanguage, setSelectedLanguage] = useState('en');
    const [activeTab, setActiveTab] = useState('All');
    const [allTagSources, setAllTagSources] = useState<TagSource[]>([]);
    const [uniqueTags, setUniqueTags] = useState<TagData[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [isLoadingTags, setIsLoadingTags] = useState(true);
    const [tagsError, setTagsError] = useState<string | null>(null);
    const [isLoadingDetails, setIsLoadingDetails] = useState(false);
    const [detailsError, setDetailsError] = useState<string | null>(null);

    const itemsPerPage = 10;

    // Fetch Initial Data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/tags/tags/?limit=1000');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                const sources = data.results || data;
                setAllTagSources(sources);
                processTags(sources);
                setIsLoadingTags(false);
            } catch (error: any) {
                console.error('Error fetching tags:', error);
                setTagsError(error.message);
                setIsLoadingTags(false);
            }
        };

        fetchData();
    }, []);

    // Process Tags
    const processTags = (sources: TagSource[]) => {
        const tagMap = new Map<string, TagData>();

        sources.forEach(source => {
            source.tags.forEach(tagName => {
                if (!tagMap.has(tagName)) {
                    tagMap.set(tagName, { name: tagName, count: 0 });
                }
                tagMap.get(tagName)!.count++;
            });
        });

        const sortedTags = Array.from(tagMap.values()).sort((a, b) => a.name.localeCompare(b.name));
        setUniqueTags(sortedTags);
    };

    // Filter and Paginate Tags
    const getPaginatedTags = () => {
        const filteredTags = uniqueTags.filter(tag =>
            tag.name.toLowerCase().includes(searchQuery.toLowerCase())
        );

        const total = Math.ceil(filteredTags.length / itemsPerPage);
        if (total !== totalPages && total !== 0) {
            // Avoid infinite loop, only set if changed
            // But we can't set state during render easily without useEffect
        }

        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        return filteredTags.slice(startIndex, endIndex);
    };

    // Effect to update total pages when filter changes
    useEffect(() => {
        const filteredTags = uniqueTags.filter(tag =>
            tag.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
        const total = Math.ceil(filteredTags.length / itemsPerPage);
        setTotalPages(total || 1);
        // Reset to page 1 if search changes
        if (currentPage > total && total > 0) {
            setCurrentPage(1);
        }
    }, [searchQuery, uniqueTags, currentPage]);


    // Handlers
    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchQuery(e.target.value);
        setCurrentPage(1);
    };

    const selectTag = (tag: TagData) => {
        setSelectedTag(tag);
        setSelectedSource(null);
        setSelectedDetailNode(null);
        setActiveTab('All');
    };

    const selectSource = (source: TagSource) => {
        setSelectedSource(source);
        fetchNodeDetails(source.source_type, source.source_id);
    };

    const fetchNodeDetails = async (type: string, id: string) => {
        setIsLoadingDetails(true);
        setDetailsError(null);
        setSelectedDetailNode(null);

        let endpoint = '';
        switch (type) {
            case 'Topic': endpoint = 'topics'; break;
            case 'Thought': endpoint = 'thoughts'; break;
            case 'Quote': endpoint = 'quotes'; break;
            case 'Passage': endpoint = 'passages'; break;
            default: endpoint = 'thoughts';
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/${endpoint}/${id}/`);
            if (!response.ok) throw new Error('Failed to fetch details');
            const data = await response.json();
            setSelectedDetailNode(data);
        } catch (error: any) {
            console.error('Error fetching details:', error);
            setDetailsError('Error loading content');
        } finally {
            setIsLoadingDetails(false);
        }
    };

    // Pagination Handlers
    const nextPage = () => {
        if (currentPage < totalPages) setCurrentPage(p => p + 1);
    };

    const prevPage = () => {
        if (currentPage > 1) setCurrentPage(p => p - 1);
    };

    const firstPage = () => setCurrentPage(1);
    const lastPage = () => setCurrentPage(totalPages);

    // Helpers
    const getIcon = (type: string) => {
        switch (type) {
            case 'Quote': return <MessageSquare className="w-3 h-3" />;
            case 'Passage': return <Book className="w-3 h-3" />;
            case 'Topic': return <LayoutGrid className="w-3 h-3" />;
            case 'Thought': return <FileText className="w-3 h-3" />;
            default: return <FileText className="w-3 h-3" />;
        }
    };

    const getBadgeColor = (type: string) => {
        switch (type) {
            case 'Quote': return 'bg-yellow-500/20 text-yellow-400';
            case 'Passage': return 'bg-blue-500/20 text-blue-400';
            case 'Topic': return 'bg-pink-500/20 text-pink-400';
            default: return 'bg-green-500/20 text-green-400';
        }
    };

    // Render Logic for Card 02
    const getFilteredSources = () => {
        if (!selectedTag) return [];
        let sources = allTagSources.filter(source => source.tags.includes(selectedTag.name));
        if (activeTab !== 'All') {
            sources = sources.filter(source => source.source_type === activeTab);
        }
        return sources;
    };

    // Render Logic for Card 03
    const getContent = () => {
        if (!selectedDetailNode || !selectedSource) return { title: '', content: '' };

        const node = selectedDetailNode;
        const type = selectedSource.source_type;
        const lang = selectedLanguage;

        let title = '';
        let content = '';
        let contentObj = null;

        if (type === 'Topic') {
            if (node.descriptions && node.descriptions.length > 0) {
                contentObj = node.descriptions[0];
            }
        } else {
            if (node.contents && node.contents.length > 0) {
                contentObj = node.contents[0];
            }
        }

        if (contentObj) {
            title = contentObj[`${lang}_title`] || contentObj['en_title'] || node.title;
            content = contentObj[`${lang}_content`] || contentObj['en_content'] || 'No content available for this language.';
        } else {
            title = node.title;
            content = node.description || node.text || node.content || 'No content available.';
        }

        return { title, content };
    };

    const paginatedTags = getPaginatedTags();
    const filteredSources = getFilteredSources();
    const { title: detailTitle, content: detailContent } = getContent();

    const TG_Card_01 = (
        <div id="TG_Card_01" className="w-1/3 bg-card-bg rounded-2xl p-6 shadow-md border border-yellow-400 flex flex-col h-full">
            {/* Search Header */}
            <div className="mb-4">
                <h2 className="text-xl font-bold text-yellow-300 mb-4 tracking-wide">TAGS</h2>
                <div className="relative">
                    <Search className="absolute left-3 top-2.5 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search tags..."
                        value={searchQuery}
                        onChange={handleSearch}
                        className="w-full bg-gray-700 text-white pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 border border-gray-600"
                    />
                </div>
            </div>

            {/* Scrollable List */}
            <div className="flex-1 overflow-y-auto pr-2 mb-4">
                {isLoadingTags ? (
                    <div className="flex items-center justify-center h-full text-gray-500">
                        Loading tags...
                    </div>
                ) : tagsError ? (
                    <div className="text-red-500 text-center p-4">
                        <p className="font-bold mb-2">Error loading tags</p>
                        <p className="text-sm">{tagsError}</p>
                    </div>
                ) : paginatedTags.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">No tags found matching "{searchQuery}"</div>
                ) : (
                    paginatedTags.map(tag => (
                        <div
                            key={tag.name}
                            onClick={() => selectTag(tag)}
                            className={`py-1.5 px-3 mb-2 rounded-lg cursor-pointer transition-colors hover:bg-gray-700 flex justify-between items-center ${selectedTag?.name === tag.name ? 'bg-blue-900/50 border border-blue-500' : 'bg-gray-800/50 border border-transparent'
                                }`}
                        >
                            <span className="font-medium text-base text-gray-200">{tag.name}</span>
                            <span className="bg-gray-600 text-xs px-2 py-1 rounded-full text-gray-300">{tag.count}</span>
                        </div>
                    ))
                )}
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-700 text-sm">
                <div className="flex gap-2">
                    <button
                        onClick={firstPage}
                        disabled={currentPage === 1}
                        className="px-3 py-1 rounded bg-gray-700 text-yellow-400 hover:bg-gray-600 disabled:text-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <ChevronsLeft className="w-4 h-4" />
                    </button>
                    <button
                        onClick={prevPage}
                        disabled={currentPage === 1}
                        className="px-3 py-1 rounded bg-gray-700 text-yellow-400 hover:bg-gray-600 disabled:text-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Previous
                    </button>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={prevPage}
                        disabled={currentPage === 1}
                        className="px-2 py-1 rounded bg-gray-700 text-yellow-400 hover:bg-gray-600 disabled:text-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <ChevronLeft className="w-4 h-4" />
                    </button>
                    <span className="text-gray-400">Page {currentPage} of {totalPages}</span>
                    <button
                        onClick={nextPage}
                        disabled={currentPage === totalPages || totalPages === 0}
                        className="px-2 py-1 rounded bg-gray-700 text-yellow-400 hover:bg-gray-600 disabled:text-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={nextPage}
                        disabled={currentPage === totalPages || totalPages === 0}
                        className="px-3 py-1 rounded bg-gray-700 text-yellow-400 hover:bg-gray-600 disabled:text-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Next
                    </button>
                    <button
                        onClick={lastPage}
                        disabled={currentPage === totalPages || totalPages === 0}
                        className="px-3 py-1 rounded bg-gray-700 text-yellow-400 hover:bg-gray-600 disabled:text-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <ChevronsRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );

    const TG_Card_02 = (
        <div id="TG_Card_02" className="flex-1 bg-card-bg rounded-2xl p-6 shadow-md border border-yellow-400 flex flex-col overflow-hidden">
            {!selectedTag ? (
                <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                    <Hash className="mb-4 opacity-20 w-16 h-16" />
                    <p className="text-xl">Select a tag to view associated content</p>
                </div>
            ) : (
                <>
                    <div className="pb-4 border-b border-gray-700 mb-4">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <Hash className="text-blue-400 w-6 h-6" />
                                <h2 className="text-2xl font-bold text-yellow-300 mb-0 tracking-wide">ITEMS</h2>
                            </div>
                            <span className="text-gray-400 text-sm">{filteredSources.length} items</span>
                        </div>

                        <div className="flex gap-2">
                            {['All', 'Topic', 'Thought', 'Quote', 'Passage'].map(tab => (
                                <button
                                    key={tab}
                                    onClick={() => setActiveTab(tab)}
                                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${activeTab === tab
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                        }`}
                                >
                                    {tab}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2">
                        <div className="grid grid-cols-1 gap-3">
                            {filteredSources.length === 0 ? (
                                <div className="text-center py-12 text-gray-500">
                                    No {activeTab === 'All' ? 'items' : activeTab.toLowerCase() + 's'} found for this tag.
                                </div>
                            ) : (
                                filteredSources.map(source => {
                                    const isSelected = selectedSource?.source_id === source.source_id && selectedSource?.source_type === source.source_type;
                                    return (
                                        <div
                                            key={`${source.source_type}_${source.source_id}`}
                                            onClick={() => selectSource(source)}
                                            className={`p-4 rounded-xl border cursor-pointer transition-all ${isSelected
                                                ? 'bg-blue-900/30 border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.2)]'
                                                : 'bg-gray-800 border-gray-700 hover:border-gray-500'
                                                }`}
                                        >
                                            <div className="flex items-center gap-2 mb-2">
                                                <span className={`p-1 rounded-md ${getBadgeColor(source.source_type)}`}>
                                                    {getIcon(source.source_type)}
                                                </span>
                                                <span className="text-xs font-semibold text-gray-200 uppercase tracking-wider">{source.source_type}</span>
                                            </div>
                                            <h3 className="text-lg font-bold text-white truncate">{source.name}</h3>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    );

    const TG_Card_03 = (
        <div id="TG_Card_03" className="flex-1 bg-card-bg rounded-2xl p-6 shadow-md border border-yellow-400 flex flex-col overflow-hidden">
            {!selectedDetailNode ? (
                isLoadingDetails ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400 mb-4"></div>
                        <p>Loading content...</p>
                    </div>
                ) : detailsError ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-red-400">
                        <AlertCircle className="mb-4 w-12 h-12" />
                        <p>{detailsError}</p>
                    </div>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                        <FileText className="mb-4 opacity-20 w-16 h-16" />
                        <p className="text-xl">Select a node above to view details</p>
                    </div>
                )
            ) : (
                <div className="h-full flex flex-col">
                    <div className="pb-4 border-b border-gray-700 mb-4 flex justify-between items-center">
                        <div>
                            <h3 className="text-sm font-bold text-yellow-300 uppercase tracking-wide mb-1">CONTENT / DESCRIPTION</h3>
                        </div>
                        <div>
                            <select
                                value={selectedLanguage}
                                onChange={(e) => setSelectedLanguage(e.target.value)}
                                className="bg-gray-700 text-white text-sm rounded-lg px-3 py-1.5 border border-gray-600 focus:outline-none focus:border-blue-500"
                            >
                                <option value="en">English</option>
                                <option value="es">Spanish</option>
                                <option value="fr">French</option>
                                <option value="hi">Hindi</option>
                                <option value="zh">Chinese</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto">
                        <div className="mb-6">
                            <h1 className="text-3xl font-bold text-white mb-4">{detailTitle}</h1>

                            <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700 text-gray-300 text-sm leading-normal pt-1 whitespace-pre-wrap">
                                {detailContent}
                            </div>
                        </div>

                        {selectedDetailNode.tags && (
                            <div className="mt-6 pt-6 border-t border-gray-700">
                                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Tags</h4>
                                <div className="flex flex-wrap gap-2">
                                    {selectedDetailNode.tags.map(t => (
                                        <span key={t} className="px-2 py-1 rounded-full bg-blue-900/30 text-blue-400 border border-blue-900 text-xs">
                                            {t}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );

    return (
        <div className="flex-1 flex flex-col h-[calc(100%+30px)] -mt-[30px] overflow-hidden">
            {/* Main Content Area */}
            <main className="flex-1 overflow-hidden w-full box-border bg-content-bg flex flex-col p-6">
                <div className="flex h-full w-full gap-6">
                    {TG_Card_01}
                    <div className="flex-1 flex flex-col gap-6 h-full">
                        {TG_Card_02}
                        {TG_Card_03}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Tags;
