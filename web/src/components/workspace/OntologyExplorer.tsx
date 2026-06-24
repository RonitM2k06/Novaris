'use client';

import React, { useEffect, useState } from 'react';
import { ReactFlow, Background, Controls, Node, Edge, MarkerType } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useWorkspaceStore } from '../../store/workspace';

export default function OntologyExplorer() {
  const { setContextData } = useWorkspaceStore();
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    const fetchOntology = async () => {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      try {
        const res = await fetch(`${API_URL}/ontology`);
        const data = await res.json();
        
        const mappedNodes: Node[] = data.nodes.map((n: any, idx: number) => ({
          id: n.id,
          position: { x: (idx % 3) * 300, y: Math.floor(idx / 3) * 150 },
          data: { label: n.name },
          style: { 
            background: '#0B1020', 
            color: '#E5E7EB', 
            border: `1px solid ${n.category === 'Policy' ? '#3B82F6' : '#1E293B'}`, 
            width: 180 
          }
        }));
        
        const mappedEdges: Edge[] = data.edges.map((e: any, idx: number) => ({
          id: `e-${idx}`,
          source: e.source,
          target: e.target,
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed, color: e.strength > 0 ? '#00FF41' : '#EF4444' },
          style: { stroke: e.strength > 0 ? '#00FF41' : '#EF4444' }
        }));

        setNodes(mappedNodes);
        setEdges(mappedEdges);

        setContextData({
          'Graph Ontology': {
            'Total Nodes': data.nodes.length,
            'Total Edges': data.edges.length,
            'Density': 'Sparse-Hierarchical'
          },
          'Selection context': {
            'Mode': 'View Only',
            'Layout': 'Auto Grid'
          }
        });
      } catch (err) {
        // Silent fail on error
      }
    };
    
    fetchOntology();
  }, [setContextData]);

  return (
    <div className="w-full h-full relative bg-[#05070D]">
      <div className="absolute top-8 left-8 z-10">
        <h2 className="text-xl font-bold tracking-widest text-[var(--color-primary-text)]">ONTOLOGY EXPLORER</h2>
      </div>
      <ReactFlow 
        nodes={nodes} 
        edges={edges}
        fitView
        className="bg-[#05070D]"
      >
        <Background color="#1E293B" gap={16} />
        <Controls className="bg-[var(--color-panel)] border-[var(--color-edge)] fill-white" />
      </ReactFlow>
    </div>
  );
}
