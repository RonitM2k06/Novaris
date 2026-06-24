from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
from .state import ScenarioState

@dataclass
class ExplanationTrace:
    scenario_id: str
    shock: Dict[str, Any]
    affected_nodes: List[str]
    causal_chain: List[Dict[str, Any]]
    impact_attribution: Dict[str, List[Dict[str, Any]]]
    summary: str

class ExplainabilityEngine:
    """Converts raw simulation traces into human-readable policy narratives."""
    
    def __init__(self, scenario: ScenarioState):
        self.scenario = scenario
        self.history = scenario.history
        self._build_causal_graph()
        
    def _build_causal_graph(self):
        """Builds a reverse lookup mapping node changes to their causes."""
        # node_id -> list of history events where it was changed
        self.node_changes = defaultdict(list)
        # Identify the initial shock
        self.initial_shock = None
        
        for entry in self.history:
            self.node_changes[entry['node_id']].append(entry)
            if entry['cause_id'] == "USER_SHOCK":
                self.initial_shock = entry

    def calculate_impact_attribution(self, target_node: str) -> List[Dict[str, Any]]:
        """Calculates the top contributing factors to a node's cumulative change."""
        contributors = defaultdict(float)
        
        for change in self.node_changes.get(target_node, []):
            cause = change['cause_id']
            if cause and cause != "USER_SHOCK":
                # Absolute value change contributed by this cause
                abs_change = change['new_value'] - change['old_value']
                contributors[cause] += abs_change
                
        # Total absolute change
        total_abs_change = sum(abs(v) for v in contributors.values())
        if total_abs_change == 0:
            return []
            
        attribution = []
        for cause, value in contributors.items():
            pct_contribution = (value / total_abs_change) * 100 if value > 0 else (abs(value) / total_abs_change) * 100
            attribution.append({
                'cause': cause,
                'raw_contribution': value,
                'pct_contribution': pct_contribution
            })
            
        # Sort by impact percentage descending
        attribution.sort(key=lambda x: x['pct_contribution'], reverse=True)
        return attribution[:3] # Top 3

    def reconstruct_path(self, target_node: str) -> List[Dict[str, Any]]:
        """Finds the strongest causal pathway from the shock to the target node."""
        if not self.initial_shock or target_node == self.initial_shock['node_id']:
            return []
            
        # A simple back-trace prioritizing the largest delta causes
        path = []
        current_node = target_node
        visited = set()
        
        while current_node and current_node != self.initial_shock['node_id']:
            if current_node in visited:
                break
            visited.add(current_node)
            
            # Find the cause that had the biggest impact on current_node
            biggest_cause = None
            max_impact = 0.0
            
            for change in self.node_changes.get(current_node, []):
                impact = abs(change['new_value'] - change['old_value'])
                if impact >= max_impact and change['cause_id'] != "USER_SHOCK":
                    max_impact = impact
                    biggest_cause = change['cause_id']
                    
            if biggest_cause:
                path.insert(0, {
                    'from': biggest_cause,
                    'to': current_node,
                    'impact': max_impact
                })
                current_node = biggest_cause
            else:
                break
                
        return path

    def _format_node_name(self, node_id: str) -> str:
        node = self.scenario.graph.get_node(node_id)
        return node.name if node else node_id

    def generate_narrative(self, target_node: str) -> str:
        """Generates a structured policy explanation."""
        if not self.initial_shock:
            return "No shock detected in simulation."
            
        changes = self.node_changes.get(target_node, [])
        if not changes:
            return f"No observed changes in {self._format_node_name(target_node)}."
            
        initial_val = changes[0]['old_value']
        final_val = changes[-1]['new_value']
        net_pct = ((final_val - initial_val) / initial_val) * 100
        
        direction = "increased" if net_pct > 0 else "decreased"
        shock_node_name = self._format_node_name(self.initial_shock['node_id'])
        shock_dir = "an increase" if self.initial_shock['delta_pct'] > 0 else "a decrease"
        
        narrative = [
            f"{self._format_node_name(target_node)} {direction} by {abs(net_pct):.2f}%.",
            f"\nThe primary driver was {shock_dir} in {shock_node_name}."
        ]
        
        path = self.reconstruct_path(target_node)
        for step in path:
            cause_name = self._format_node_name(step['from'])
            target_name = self._format_node_name(step['to'])
            
            # Determine direction of cause
            cause_changes = self.node_changes.get(step['from'], [])
            if cause_changes:
                cause_net = cause_changes[-1]['new_value'] - cause_changes[0]['old_value']
                cause_dir = "increased" if cause_net > 0 else "contracted"
                narrative.append(f"{cause_name} {cause_dir}.")
                
        narrative.append(f"The combined effect drove the change in {self._format_node_name(target_node)}.")
        return "\n".join(narrative)

    def explain(self, target_node: str) -> ExplanationTrace:
        """Generates the full explanation object for a given node outcome."""
        return ExplanationTrace(
            scenario_id=self.scenario.name,
            shock=self.initial_shock,
            affected_nodes=list(self.node_changes.keys()),
            causal_chain=self.reconstruct_path(target_node),
            impact_attribution={target_node: self.calculate_impact_attribution(target_node)},
            summary=self.generate_narrative(target_node)
        )

class ScenarioComparisonEngine:
    """Compares two different economic scenarios to highlight diverging outcomes."""
    
    @staticmethod
    def compare(scenario_a: ScenarioState, scenario_b: ScenarioState, target_nodes: List[str]) -> str:
        report = [
            f"=== Scenario Comparison ===",
            f"Scenario A: {scenario_a.name}",
            f"Scenario B: {scenario_b.name}\n",
            "--- Diverging Outcomes ---"
        ]
        
        for node_id in target_nodes:
            node_name = scenario_a.graph.get_node(node_id).name if scenario_a.graph.get_node(node_id) else node_id
            
            # Calculate A
            changes_a = [e for e in scenario_a.history if e['node_id'] == node_id]
            pct_a = 0.0
            if changes_a:
                pct_a = ((changes_a[-1]['new_value'] - changes_a[0]['old_value']) / changes_a[0]['old_value']) * 100
                
            # Calculate B
            changes_b = [e for e in scenario_b.history if e['node_id'] == node_id]
            pct_b = 0.0
            if changes_b:
                pct_b = ((changes_b[-1]['new_value'] - changes_b[0]['old_value']) / changes_b[0]['old_value']) * 100
                
            report.append(f"* {node_name}:")
            report.append(f"  - Scenario A: {pct_a:+.2f}%")
            report.append(f"  - Scenario B: {pct_b:+.2f}%")
            
        return "\n".join(report)
