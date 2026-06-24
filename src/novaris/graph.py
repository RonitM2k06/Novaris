from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Node:
    """Represents a macroeconomic indicator or sector."""
    id: str
    name: str
    base_value: float
    current_value: float = 0.0
    category: str = "indicator"

    def __post_init__(self):
        if self.current_value == 0.0:
            self.current_value = self.base_value

@dataclass
class Edge:
    """Represents a causal relationship between two nodes."""
    source_id: str
    target_id: str
    strength: float     # Magnitude of effect (e.g. elasticity)
    confidence: float   # Probability or R-squared score
    lag: float          # Time delay for effect to propagate

class EconomicGraph:
    """The foundational knowledge graph storing entities and their relations."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency_list: Dict[str, List[Edge]] = {}

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        if node.id not in self.adjacency_list:
            self.adjacency_list[node.id] = []

    def add_edge(self, edge: Edge):
        self.edges.append(edge)
        self.adjacency_list[edge.source_id].append(edge)
        
    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)
        
    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        return self.adjacency_list.get(node_id, [])
