from collections import deque
import math
from .state import ScenarioState

class NonlinearSimulationEngine:
    """Propagates economic shocks using nonlinear response functions (Saturation, Substitution, Inertia)."""
    
    def __init__(self, scenario: ScenarioState):
        self.scenario = scenario
        
    def _apply_nonlinear_transform(self, target_id: str, raw_effect_pct: float) -> float:
        """Applies mathematical dampening to extreme shocks."""
        
        # 1. Behavioral Inertia
        # Consumer Confidence adjusts slowly; it caps out per time-step.
        if target_id == "consumer_confidence":
            max_inertia_cap = 0.15 # Max 15% swing per step
            if raw_effect_pct > max_inertia_cap: return max_inertia_cap
            if raw_effect_pct < -max_inertia_cap: return -max_inertia_cap
            
        # 2. Saturation & Substitution Effects (using hyperbolic tangent)
        # As shocks get extremely large, actors substitute or system saturates.
        # We limit the mathematical pass-through.
        # For example, an energy shock of +150% shouldn't pass through linearly.
        # tanh(x / cap) * cap bounds the effect smoothly at `cap`.
        
        # Determine the maximum allowable fractional change for general nodes
        saturation_cap = 0.25 # Standard nodes saturate around a 25% single-step shock
        
        if target_id == "energy_prices" or target_id == "inflation":
            # Energy substitution kicks in around +30%
            saturation_cap = 0.30
            
        # Apply smooth asymptotic saturation
        dampened_effect = saturation_cap * math.tanh(raw_effect_pct / saturation_cap)
        
        return dampened_effect

    def inject_shock(self, node_id: str, delta_pct: float):
        """Injects an anomaly into the system with initial nonlinearity."""
        node = self.scenario.graph.get_node(node_id)
        if not node:
            raise ValueError(f"Node '{node_id}' not found in the graph.")
            
        old_val = node.current_value
        
        # The initial shock itself might be purely exogenous (like Oil +150%),
        # so we don't dampen the USER shock, only its downstream effects.
        new_val = old_val * (1.0 + delta_pct)
        node.current_value = new_val
        
        self.scenario.record_history(node_id, old_val, new_val, cause_id="USER_SHOCK")
        
        queue = deque([(node_id, delta_pct, 0.0)])
        self._propagate(queue)

    def _propagate(self, queue: deque, max_steps: int = 10, attenuation_factor: float = 0.8):
        while queue and self.scenario.time_step < max_steps:
            current_id, delta, current_lag = queue.popleft()
            
            if abs(delta) < 0.001:
                continue
                
            outgoing = self.scenario.graph.get_outgoing_edges(current_id)
            for edge in outgoing:
                target = self.scenario.graph.get_node(edge.target_id)
                if not target:
                    continue
                    
                # 3. Policy Dampening
                # If inflation spikes, government intervention automatically scales non-linearly
                if target.id == "inflation" and delta > 0.10 and current_id != "government_intervention":
                    # Synthetic policy dampening - inflation is artificially suppressed by emergency subsidies
                    edge_strength = edge.strength * 0.5 
                else:
                    edge_strength = edge.strength
                
                # Raw linear calculation
                raw_effect_pct = delta * edge_strength * edge.confidence
                
                # Apply Nonlinear Transforms
                nonlinear_effect_pct = self._apply_nonlinear_transform(target.id, raw_effect_pct)
                
                # Systemic time attenuation
                final_effect_pct = nonlinear_effect_pct * attenuation_factor
                
                old_val = target.current_value
                new_val = old_val * (1.0 + final_effect_pct)
                target.current_value = new_val
                
                self.scenario.record_history(
                    target.id, 
                    old_val, 
                    new_val, 
                    cause_id=current_id
                )
                
                queue.append((target.id, final_effect_pct, current_lag + edge.lag))
                
            self.scenario.time_step += 1
