import math
from collections import deque
from novaris.state import ScenarioState
from novaris.nonlinear_simulation import NonlinearSimulationEngine

class AdaptiveExpectationModel:
    """Models how actors slowly adapt to economic realities over multiple time steps."""
    def __init__(self):
        self.history_memory = {}
        
    def adapt(self, node_id: str, new_shock: float) -> float:
        if node_id not in self.history_memory:
            self.history_memory[node_id] = 0.0
        
        # Agents adapt: expectation is a blend of past memory (70%) and new reality (30%)
        adapted_shock = (self.history_memory[node_id] * 0.7) + (new_shock * 0.3)
        self.history_memory[node_id] = adapted_shock
        return adapted_shock

class AsymmetricResponseFunction:
    """Applies asymmetric bounds, where upward shocks scale differently than downward shocks."""
    @staticmethod
    def apply(node_id: str, raw_effect_pct: float) -> float:
        if node_id == "inflation":
            # Sticky Prices: Deflation is extremely bounded.
            if raw_effect_pct < 0:
                # Hard floor for deflation to represent sticky wages and rents
                return max(-0.025, raw_effect_pct * 0.15) 
            else:
                return raw_effect_pct
                
        if node_id == "consumer_spending":
            # Wage stickiness means nominal income doesn't drop instantly
            if raw_effect_pct < 0:
                return raw_effect_pct * 0.6
                
        return raw_effect_pct

class StickySimulationEngine(NonlinearSimulationEngine):
    """Integrates Sticky Prices, Asymmetry, and Adaptive Expectations on top of Nonlinear Dynamics."""
    def __init__(self, scenario: ScenarioState):
        super().__init__(scenario)
        self.adaptive_model = AdaptiveExpectationModel()
        
    def _apply_nonlinear_transform(self, target_id: str, raw_effect_pct: float) -> float:
        # 1. Base Nonlinear Saturation
        saturated_effect = super()._apply_nonlinear_transform(target_id, raw_effect_pct)
        
        # 2. Asymmetric Elasticity (Sticky Prices)
        asymmetric_effect = AsymmetricResponseFunction.apply(target_id, saturated_effect)
        
        # 3. Adaptive Expectations
        if target_id == "consumer_confidence":
            adapted_effect = self.adaptive_model.adapt(target_id, asymmetric_effect)
            return adapted_effect
            
        return asymmetric_effect
