import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import axios from 'axios';

interface Node extends d3.SimulationNodeDatum {
    id: string;
    labels: string[];
    name: string;
    type: string;
    size?: number;
    tags?: string[];
}

interface Link extends d3.SimulationLinkDatum<Node> {
    source: string | Node;
    target: string | Node;
    type: string;
}

interface GraphData {
    nodes: Node[];
    links: Link[];
}

const GraphView: React.FC = () => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [fullData, setFullData] = useState<GraphData | null>(null); // Store full dataset
    const [filteredData, setFilteredData] = useState<GraphData | null>(null); // Store filtered dataset
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedType, setSelectedType] = useState<string>('ALL');
    const [nodeDetail, setNodeDetail] = useState<Node | null>(null);

    // Adjust width for 75% container (approximate, responsive logic handles actual resize)
    const width = 800; // Adjusted based on layout
    const height = 600;

    const colorScale: { [key: string]: string } = {
        'TOPIC': '#8B5CF6',
        'THOUGHT': '#10B981',
        'QUOTE': '#F59E0B',
        'PASSAGE': '#3B82F6',
        'CONTENT': '#EF4444',
        'DESCRIPTION': '#6B7280'
    };

    // Button configuration
    const filterButtons = [
        { id: 'btn_all', label: 'All', type: 'ALL', color: '#FFFFFF' },
        { id: 'btn_topics', label: 'Topics', type: 'TOPIC', color: colorScale['TOPIC'] },
        { id: 'btn_thoughts', label: 'Thoughts', type: 'THOUGHT', color: colorScale['THOUGHT'] },
        { id: 'btn_quotes', label: 'Quotes', type: 'QUOTE', color: colorScale['QUOTE'] },
        { id: 'btn_passages', label: 'Passages', type: 'PASSAGE', color: colorScale['PASSAGE'] },
        { id: 'btn_contents', label: 'Contents', type: 'CONTENT', color: colorScale['CONTENT'] },
        { id: 'btn_desc', label: 'Descriptions', type: 'DESCRIPTION', color: colorScale['DESCRIPTION'] },
    ];

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('/graph/api/data/');
                const nodes = response.data.nodes.map((n: any) => ({
                    ...n,
                    name: n.name || n.title || n.id
                }));

                const nodeIds = new Set(nodes.map((n: any) => n.id));
                const links = response.data.links
                    .filter((l: any) => nodeIds.has(l.source) && nodeIds.has(l.target))
                    .map((l: any) => ({ ...l }));

                const data = { nodes, links };
                setFullData(data);
                setFilteredData(data); // Initially show all
                setLoading(false);
            } catch (err) {
                console.error('Error fetching graph data:', err);
                setError('Failed to load graph data');
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Filtering Logic
    useEffect(() => {
        if (!fullData) return;

        if (selectedType === 'ALL') {
            setFilteredData(fullData);
        } else {
            // Filter nodes by type
            const nodes = fullData.nodes.filter(n => n.type === selectedType);
            const nodeIds = new Set(nodes.map(n => n.id));

            // Filter links where both source and target are in the filtered nodes
            // Note: D3 mutates links to use objects for source/target, so we need to handle both cases or ensure fresh copies
            // Since we setFilteredData, we should probably derive from fresh fullData to avoid reference issues
            // Ideally, we re-process fullData links

            // Re-map fullData links to check against IDs. 
            // Warning: fullData.links might have been mutated by previous D3 simulation if we passed it directly.
            // Best practice: Deep copy for simulation usage. But here we might rely on the fact that we are creating a new object for filteredData

            // Keep it simple: Filter based on IDs assuming source/target might be objects or strings
            const links = fullData.links.filter(l => {
                const sourceId = typeof l.source === 'object' ? (l.source as any).id : l.source;
                const targetId = typeof l.target === 'object' ? (l.target as any).id : l.target;
                return nodeIds.has(sourceId) && nodeIds.has(targetId);
            });

            setFilteredData({ nodes: nodes.map(n => ({ ...n })), links: links.map(l => ({ ...l })) });
        }
    }, [selectedType, fullData]);

    // D3 Rendering
    useEffect(() => {
        if (!filteredData || !svgRef.current) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        // Use a clone to avoid mutating state directly in repeated simulations
        const simulationNodes = filteredData.nodes.map(d => ({ ...d }));
        const simulationLinks = filteredData.links.map(d => ({ ...d }));

        const simulation = d3.forceSimulation<Node>(simulationNodes)
            .force('link', d3.forceLink<Node, Link>(simulationLinks).id((d: any) => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));

        const link = svg.append('g')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .selectAll('line')
            .data(simulationLinks)
            .join('line')
            .attr('stroke-width', 1);

        const node = svg.append('g')
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .selectAll('circle')
            .data(simulationNodes)
            .join('circle')
            .attr('r', (d: Node) => Math.sqrt((d.size || 10) * 3) * 2)
            .attr('fill', (d: Node) => colorScale[d.type] || '#666')
            .call(d3.drag<SVGCircleElement, Node>()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended) as any)
            .on('click', (event, d) => {
                setNodeDetail(d);
            });

        const label = svg.append('g')
            .selectAll('text')
            .data(simulationNodes)
            .join('text')
            .text((d: Node) => d.name || d.id)
            .style('font-size', '10px')
            .style('font-family', 'Arial, sans-serif')
            .style('fill', '#f9fafb')
            .style('text-anchor', 'middle')
            .style('dominant-baseline', 'central')
            .style('pointer-events', 'none');

        node.append('title')
            .text((d: Node) => `${d.type}: ${d.name || d.id}`);

        simulation.on('tick', () => {
            link
                .attr('x1', (d: any) => d.source.x)
                .attr('y1', (d: any) => d.source.y)
                .attr('x2', (d: any) => d.target.x)
                .attr('y2', (d: any) => d.target.y);

            node
                .attr('cx', (d: Node) => d.x!)
                .attr('cy', (d: Node) => d.y!);

            label
                .attr('x', (d: Node) => d.x!)
                .attr('y', (d: Node) => d.y! + 20);
        });

        function dragstarted(event: d3.D3DragEvent<SVGCircleElement, Node, Node>) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event: d3.D3DragEvent<SVGCircleElement, Node, Node>) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event: d3.D3DragEvent<SVGCircleElement, Node, Node>) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        const zoom = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                svg.selectAll('g').attr('transform', event.transform);
            });

        svg.call(zoom);

        return () => {
            simulation.stop();
        };
    }, [filteredData]); // Re-run when filtered data changes

    return (
        <div className="container mx-auto !p-4">
            <div className="flex flex-col lg:flex-row gap-6">

                {/* GV_Card_01: Graph View (75%) */}
                <div className="GV_Card_01 w-full lg:w-3/4 card p-4 flex flex-col">
                    <div className="flex flex-col sm:flex-row justify-between items-center mb-4 gap-4">
                        <h1 className="text-xl font-bold text-gray-100">Graph View</h1>

                        {/* Legend / Filter Buttons */}
                        <div className="flex flex-wrap gap-2 justify-end">
                            {filterButtons.map((btn) => (
                                <button
                                    key={btn.id}
                                    id={btn.id}
                                    onClick={() => setSelectedType(btn.type)}
                                    disabled={selectedType === btn.type}
                                    className={`px-3 py-1 rounded-full text-xs font-medium transition-opacity ${selectedType === btn.type
                                            ? 'opacity-50 cursor-not-allowed ring-2 ring-white'
                                            : 'hover:opacity-80'
                                        }`}
                                    style={{
                                        backgroundColor: btn.color,
                                        color: btn.type === 'ALL' ? '#000' : '#FFF'
                                    }}
                                >
                                    {btn.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="border border-gray-700 rounded overflow-hidden bg-gray-800 relative flex-grow" style={{ minHeight: '600px' }}>
                        {loading && (
                            <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                                Loading graph data...
                            </div>
                        )}
                        {error && (
                            <div className="absolute inset-0 flex items-center justify-center text-red-500">
                                {error}
                            </div>
                        )}
                        <svg ref={svgRef} width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} className="block"></svg>
                    </div>

                    <div className="text-sm text-gray-400 mt-2 text-right">
                        {filteredData ? (
                            <span>{filteredData.nodes.length} nodes, {filteredData.links.length} connections</span>
                        ) : '...'}
                    </div>
                </div>

                {/* GV_Card_02: Node Detail (25%) */}
                <div className="GV_Card_02 w-full lg:w-1/4 card p-4 flex flex-col">
                    <h2 className="text-xl font-bold text-gray-100 mb-4">Node Detail</h2>

                    {nodeDetail ? (
                        <div className="flex flex-col gap-4 text-gray-300">
                            <div>
                                <span className="text-xs text-gray-500 uppercase">Type</span>
                                <div className="font-medium text-white" style={{ color: colorScale[nodeDetail.type] }}>
                                    {nodeDetail.type}
                                </div>
                            </div>

                            <div>
                                <span className="text-xs text-gray-500 uppercase">Name/Title</span>
                                <div className="font-lg text-white break-words">
                                    {nodeDetail.name}
                                </div>
                            </div>

                            {nodeDetail.labels && (
                                <div>
                                    <span className="text-xs text-gray-500 uppercase">Labels</span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        {nodeDetail.labels.map((l: string, i: number) => (
                                            <span key={i} className="bg-gray-700 px-2 py-0.5 rounded text-xs">
                                                {l}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {nodeDetail.id && (
                                <div>
                                    <span className="text-xs text-gray-500 uppercase">ID</span>
                                    <div className="text-xs font-mono bg-gray-900 p-1 rounded break-all">
                                        {nodeDetail.id}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-gray-500 italic text-center mt-10">
                            Click on a node to view details
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default GraphView;
