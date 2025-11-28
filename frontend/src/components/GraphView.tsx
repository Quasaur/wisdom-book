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
    const [data, setData] = useState<GraphData | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const width = 1160;
    const height = 600;

    const colorScale: { [key: string]: string } = {
        'TOPIC': '#8B5CF6',
        'THOUGHT': '#10B981',
        'QUOTE': '#F59E0B',
        'PASSAGE': '#3B82F6',
        'CONTENT': '#EF4444',
        'DESCRIPTION': '#6B7280'
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('/graph/api/data/');
                // Transform links to match D3 expectation (source/target as IDs initially)
                const nodes = response.data.nodes.map((n: any) => ({ ...n }));
                const links = response.data.links.map((l: any) => ({ ...l }));
                setData({ nodes, links });
                setLoading(false);
            } catch (err) {
                console.error('Error fetching graph data:', err);
                setError('Failed to load graph data');
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    useEffect(() => {
        if (!data || !svgRef.current) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove(); // Clear previous render

        // Create simulation
        const simulation = d3.forceSimulation<Node>(data.nodes)
            .force('link', d3.forceLink<Node, Link>(data.links).id((d: any) => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));

        // Create links
        const link = svg.append('g')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .selectAll('line')
            .data(data.links)
            .join('line')
            .attr('stroke-width', 1);

        // Create nodes
        const node = svg.append('g')
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .selectAll('circle')
            .data(data.nodes)
            .join('circle')
            .attr('r', (d: Node) => Math.sqrt((d.size || 10) * 3))
            .attr('fill', (d: Node) => colorScale[d.type] || '#666')
            .call(d3.drag<SVGCircleElement, Node>()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended) as any);

        // Add labels
        const label = svg.append('g')
            .selectAll('text')
            .data(data.nodes)
            .join('text')
            .text((d: Node) => d.name || d.id)
            .style('font-size', '10px')
            .style('font-family', 'Arial, sans-serif')
            .style('fill', '#f9fafb')
            .style('text-anchor', 'middle')
            .style('dominant-baseline', 'central')
            .style('pointer-events', 'none');

        // Add tooltips
        node.append('title')
            .text((d: Node) => `${d.type}: ${d.name || d.id}${d.tags ? '\nTags: ' + d.tags.join(', ') : ''}`);

        // Update positions on simulation tick
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

        // Drag functions
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

        return () => {
            simulation.stop();
        };
    }, [data]);

    return (
        <div className="container mx-auto p-4 bg-gray-900 text-gray-100 rounded-lg shadow-lg">
            <div className="text-center mb-4">
                <h1 className="text-2xl font-bold">Knowledge Graph Visualization</h1>
                <p className="text-gray-400">Interactive visualization of connections between topics, thoughts, quotes, and passages</p>
            </div>

            <div className="flex justify-between items-center mb-4">
                <div className="text-sm text-gray-300">
                    {data ? (
                        <>
                            <span className="font-bold">{data.nodes.length}</span> nodes,
                            <span className="font-bold ml-1">{data.links.length}</span> connections
                        </>
                    ) : (
                        <span>Loading stats...</span>
                    )}
                </div>
                <div className="flex gap-4 text-xs">
                    {Object.entries(colorScale).map(([type, color]) => (
                        <div key={type} className="flex items-center gap-1">
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
                            <span>{type.charAt(0) + type.slice(1).toLowerCase()}s</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="border border-gray-700 rounded overflow-hidden bg-gray-800 relative" style={{ height: '600px' }}>
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
                <svg ref={svgRef} width={width} height={height} className="block"></svg>
            </div>
        </div>
    );
};

export default GraphView;
