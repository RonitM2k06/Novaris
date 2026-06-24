from collections import deque
from .state import ScenarioState

class SimulationEngine:
    """Propagates economic shocks through the Knowledge Graph."""
    def __init__(self, scenario: ScenarioState):
        self.scenario = scenario
        
    def inject_shock(self, node_id: str, delta_pct: float):
        """
        Injects an anomaly into the system.
        delta_pct: Fractional change (e.g., 0.20 for +20%)
        """
        node = self.scenario.graph.get_node(node_id)
        if not node:
            raise ValueError(f"Node '{node_id}' not found in the graph.")
            
        old_val = node.current_value
        new_val = old_val * (1.0 + delta_pct)
        node.current_value = new_val
        
        # Record the initial shock
        self.scenario.record_history(node_id, old_val, new_val, cause_id="USER_SHOCK")
        
        # Queue format: (source_node_id, delta_pct_caused, time_delay_accumulator)
        queue = deque([(node_id, delta_pct, 0.0)])
        self._propagate(queue)

    def _propagate(self, queue: deque, max_steps: int = 10, attenuation_factor: float = 0.8):
        """
        Traverses the graph step-by-step, applying ripple effects.
        """
        while queue and self.scenario.time_step < max_steps:
            current_id, delta, current_lag = queue.popleft()
            
            # If the shock is too small, it has been absorbed by the system
            if abs(delta) < 0.001:
                continue
                
            outgoing = self.scenario.graph.get_outgoing_edges(current_id)
            for edge in outgoing:
                target = self.scenario.graph.get_node(edge.target_id)
                if not target:
                    continue
                    
                # Calculate effect: delta of source * elasticity * certainty
                effect_pct = delta * edge.strength * edge.confidence
                
                # Apply structural attenuation to prevent infinite loops
                effect_pct *= attenuation_factor
                
                old_val = target.current_value
                new_val = old_val * (1.0 + effect_pct)
                target.current_value = new_val
                
                # Record the cascade
                self.scenario.record_history(
                    target.id, 
                    old_val, 
                    new_val, 
                    cause_id=current_id
                )
                
                # Queue the next-order effect
                queue.append((target.id, effect_pct, current_lag + edge.lag))
                
            self.scenario.time_step += 1
