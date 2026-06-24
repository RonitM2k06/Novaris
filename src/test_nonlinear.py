from novaris.historical_replay import HistoricalScenario, ExpectedOutcome, HistoricalReplayEngine
from novaris.state import StateManager
from test_ontology_expansion import build_expanded_graph
from novaris.nonlinear_simulation import NonlinearSimulationEngine

class NonlinearHistoricalReplayEngine(HistoricalReplayEngine):
    """Overrides the replay engine to use the Nonlinear Simulator."""
    def replay(self, scenario: HistoricalScenario):
        state = self.manager.create_scenario(scenario.name)
        engine = NonlinearSimulationEngine(state)
        
        for node_id, delta in scenario.initial_shocks.items():
            engine.inject_shock(node_id, delta)
            
        simulated_outcomes = {}
        for node_id in self.manager.base_graph.nodes.keys():
            history = [h for h in state.history if h['node_id'] == node_id]
            if history:
                net_change = (history[-1]['new_value'] - history[0]['old_value']) / history[0]['old_value']
                simulated_outcomes[node_id] = net_change
            else:
                simulated_outcomes[node_id] = 0.0
                
        # To avoid circular import issues, we just compute magnitude error locally
        from novaris.historical_replay import ReplayEvaluationMetrics
        metrics = ReplayEvaluationMetrics.evaluate(scenario.expected_outcomes, simulated_outcomes)
        
        return {
            "scenario": scenario,
            "simulated_outcomes": simulated_outcomes,
            "metrics": metrics
        }

def build_test_scenarios():
    return [
        HistoricalScenario(
            name="1970s Oil Embargo",
            year="1973",
            description="Massive +150% oil shock testing substitution/saturation effects.",
            initial_shocks={"oil_prices": +1.50},
            expected_outcomes=[
                ExpectedOutcome("inflation", +0.12),
                ExpectedOutcome("gdp", -0.03)
            ]
        ),
        HistoricalScenario(
            name="2022 Energy Crisis",
            year="2022",
            description="Energy spike +80% testing policy dampening.",
            initial_shocks={"oil_prices": +0.80, "government_subsidies": +0.60},
            expected_outcomes=[
                ExpectedOutcome("inflation", +0.08),
                ExpectedOutcome("manufacturing", -0.05),
                ExpectedOutcome("gdp", -0.02)
            ]
        ),
        HistoricalScenario(
            name="2008 Financial Crisis",
            year="2008",
            description="Credit & Housing collapse testing behavioral inertia.",
            initial_shocks={"housing_markets": -0.30, "credit_markets": -0.40},
            expected_outcomes=[
                ExpectedOutcome("gdp", -0.04),
                ExpectedOutcome("inflation", -0.02) # Testing deflation overshoot
            ]
        )
    ]

if __name__ == "__main__":
    graph = build_expanded_graph()
    
    linear_engine = HistoricalReplayEngine(graph)
    nonlinear_engine = NonlinearHistoricalReplayEngine(graph)
    
    scenarios = build_test_scenarios()
    
    print("=== NONLINEAR DYNAMICS VALIDATION ===")
    
    for scenario in scenarios:
        print(f"\n--- {scenario.name} ---")
        
        lin_res = linear_engine.replay(scenario)
        non_res = nonlinear_engine.replay(scenario)
        
        # Compare Magnitude Errors
        lin_err = lin_res['metrics']['magnitude_error']
        non_err = non_res['metrics']['magnitude_error']
        
        print(f"Linear Magnitude Error: {lin_err:.2f} points")
        print(f"Nonlinear Magnitude Error: {non_err:.2f} points")
        print("Outcomes:")
        for exp in scenario.expected_outcomes:
            lin_val = lin_res['simulated_outcomes'].get(exp.node_id, 0.0)
            non_val = non_res['simulated_outcomes'].get(exp.node_id, 0.0)
            print(f"  {exp.node_id}:")
            print(f"    Expected: {exp.expected_pct_change*100:+.2f}%")
            print(f"    Linear  : {lin_val*100:+.2f}%")
            print(f"    Nonlinear: {non_val*100:+.2f}%")
