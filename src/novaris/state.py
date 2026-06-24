from typing import Dict, Any, List
import copy
from .graph import EconomicGraph

class ScenarioState:
    """Holds the graph state for a specific simulation branch."""
    def __init__(self, name: str, graph: EconomicGraph):
        self.name = name
        self.graph = copy.deepcopy(graph)
        self.time_step = 0
        self.history: List[Dict[str, Any]] = [] 

    def record_history(self, node_id: str, old_val: float, new_val: float, cause_id: str = None):
        """Logs node state changes to facilitate explainability traces."""
        self.history.append({
            'time_step': self.time_step,
            'node_id': node_id,
            'old_value': old_val,
            'new_value': new_val,
            'delta_pct': (new_val - old_val) / old_val if old_val != 0 else 0,
            'cause_id': cause_id
        })

class StateManager:
    """Manages the base digital twin and its branching simulated states."""
    def __init__(self):
        self.base_graph = EconomicGraph()
        self.scenarios: Dict[str, ScenarioState] = {}
        
    def create_scenario(self, scenario_name: str) -> ScenarioState:
        """Branches the current base graph into a new experimental scenario."""
        scenario = ScenarioState(scenario_name, self.base_graph)
        self.scenarios[scenario_name] = scenario
        return scenario
        
    def get_scenario(self, scenario_name: str) -> ScenarioState:
        return self.scenarios.get(scenario_name)
