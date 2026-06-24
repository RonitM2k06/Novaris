from dataclasses import dataclass
from typing import Dict, List, Any
from novaris.state import ScenarioState, StateManager
from novaris.simulation import SimulationEngine
from novaris.graph import EconomicGraph

@dataclass
class ExpectedOutcome:
    node_id: str
    expected_pct_change: float

@dataclass
class HistoricalScenario:
    name: str
    year: str
    description: str
    initial_shocks: Dict[str, float]
    expected_outcomes: List[ExpectedOutcome]

class ReplayEvaluationMetrics:
    """Computes evaluation metrics comparing historical reality vs simulation."""
    @staticmethod
    def evaluate(expected: List[ExpectedOutcome], simulated: Dict[str, float]) -> Dict[str, Any]:
        direction_accuracy = 0
        total_error = 0.0
        
        for exp in expected:
            sim_val = simulated.get(exp.node_id, 0.0)
            
            # Direction Accuracy
            if (exp.expected_pct_change > 0 and sim_val > 0) or \
               (exp.expected_pct_change < 0 and sim_val < 0) or \
               (exp.expected_pct_change == 0 and sim_val == 0):
                direction_accuracy += 1
                
            # Magnitude Error (absolute difference in percentage points)
            total_error += abs(exp.expected_pct_change - sim_val) * 100
            
        direction_score = (direction_accuracy / len(expected)) * 100
        avg_magnitude_error = total_error / len(expected)
        
        # Agreement Score (0-100)
        agreement_score = max(0.0, direction_score - (avg_magnitude_error * 1.5))
        if direction_score < 50:
            agreement_score = 0.0
            
        return {
            "direction_accuracy": direction_score,
            "magnitude_error": avg_magnitude_error,
            "agreement_score": agreement_score
        }

class HistoricalReplayEngine:
    """Executes historical scenarios against the digital twin."""
    def __init__(self, base_graph: EconomicGraph):
        self.manager = StateManager()
        self.manager.base_graph = base_graph
        
    def replay(self, scenario: HistoricalScenario) -> Dict[str, Any]:
        state = self.manager.create_scenario(scenario.name)
        engine = SimulationEngine(state)
        
        # Inject all initial shocks simultaneously
        for node_id, delta in scenario.initial_shocks.items():
            engine.inject_shock(node_id, delta)
            
        # Calculate net simulated outcomes
        simulated_outcomes = {}
        for node_id in self.manager.base_graph.nodes.keys():
            history = [h for h in state.history if h['node_id'] == node_id]
            if history:
                net_change = (history[-1]['new_value'] - history[0]['old_value']) / history[0]['old_value']
                simulated_outcomes[node_id] = net_change
            else:
                simulated_outcomes[node_id] = 0.0
                
        metrics = ReplayEvaluationMetrics.evaluate(scenario.expected_outcomes, simulated_outcomes)
        
        return {
            "scenario": scenario,
            "simulated_outcomes": simulated_outcomes,
            "metrics": metrics
        }
