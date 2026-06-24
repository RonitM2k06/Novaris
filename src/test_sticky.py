from novaris.historical_replay import HistoricalScenario, ExpectedOutcome, HistoricalReplayEngine
from novaris.state import StateManager
from test_ontology_expansion import build_expanded_graph, build_expanded_scenarios
from test_nonlinear import NonlinearHistoricalReplayEngine
from novaris.sticky_simulation import StickySimulationEngine

class StickyHistoricalReplayEngine(HistoricalReplayEngine):
    def replay(self, scenario: HistoricalScenario):
        state = self.manager.create_scenario(scenario.name)
        engine = StickySimulationEngine(state)
        
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
                
        from novaris.historical_replay import ReplayEvaluationMetrics
        metrics = ReplayEvaluationMetrics.evaluate(scenario.expected_outcomes, simulated_outcomes)
        
        return {
            "scenario": scenario,
            "simulated_outcomes": simulated_outcomes,
            "metrics": metrics
        }

if __name__ == "__main__":
    graph = build_expanded_graph()
    
    linear_engine = HistoricalReplayEngine(graph)
    nonlinear_engine = NonlinearHistoricalReplayEngine(graph)
    sticky_engine = StickyHistoricalReplayEngine(graph)
    
    # We only care about 2008, COVID, and Oil Embargo for this test
    all_scenarios = build_expanded_scenarios()
    from test_nonlinear import build_test_scenarios
    oil_scenario = [s for s in build_test_scenarios() if "1970s" in s.name][0]
    
    scenarios_to_test = [
        [s for s in all_scenarios if "2008" in s.name][0],
        [s for s in all_scenarios if "COVID" in s.name][0],
        oil_scenario
    ]
    
    print("=== ASYMMETRIC ELASTICITY & STICKY PRICE VALIDATION ===")
    
    for scenario in scenarios_to_test:
        print(f"\n--- {scenario.name} ---")
        
        lin_res = linear_engine.replay(scenario)
        non_res = nonlinear_engine.replay(scenario)
        stk_res = sticky_engine.replay(scenario)
        
        print(f"Linear Agreement: {lin_res['metrics']['agreement_score']:.1f}")
        print(f"Nonlinear Agreement: {non_res['metrics']['agreement_score']:.1f}")
        print(f"Sticky Price Agreement: {stk_res['metrics']['agreement_score']:.1f}")
        
        print("Outcomes:")
        for exp in scenario.expected_outcomes:
            lin_val = lin_res['simulated_outcomes'].get(exp.node_id, 0.0)
            non_val = non_res['simulated_outcomes'].get(exp.node_id, 0.0)
            stk_val = stk_res['simulated_outcomes'].get(exp.node_id, 0.0)
            
            print(f"  {exp.node_id}:")
            print(f"    Expected: {exp.expected_pct_change*100:+.2f}%")
            print(f"    Linear  : {lin_val*100:+.2f}%")
            print(f"    Nonlin  : {non_val*100:+.2f}%")
            print(f"    Sticky  : {stk_val*100:+.2f}%")
