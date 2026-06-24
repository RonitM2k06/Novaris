import sys
from novaris.graph import EconomicGraph, Node, Edge
from novaris.state import StateManager
from novaris.simulation import SimulationEngine
from novaris.explainability import ExplainabilityEngine, ScenarioComparisonEngine

def build_graph() -> EconomicGraph:
    g = EconomicGraph()
    # Nodes
    g.add_node(Node("interest_rate", "Interest Rate", 5.0, category="Policy"))
    g.add_node(Node("oil_prices", "Oil Prices", 80.0, category="External"))
    g.add_node(Node("manufacturing", "Manufacturing Output", 500.0, category="Sector"))
    g.add_node(Node("consumer_spending", "Consumer Spending", 1000.0, category="Macroeconomic"))
    g.add_node(Node("employment", "Employment", 150.0, category="Macroeconomic"))
    g.add_node(Node("gdp", "GDP", 2000.0, category="Macroeconomic"))
    g.add_node(Node("energy_prices", "Energy Prices", 100.0, category="Macroeconomic"))
    g.add_node(Node("inflation", "Inflation", 3.0, category="Macroeconomic"))

    # Edges
    g.add_edge(Edge("interest_rate", "consumer_spending", strength=-0.5, confidence=0.9, lag=1.0))
    g.add_edge(Edge("interest_rate", "manufacturing", strength=-0.4, confidence=0.8, lag=2.0))
    g.add_edge(Edge("oil_prices", "energy_prices", strength=0.8, confidence=0.9, lag=0.0))
    g.add_edge(Edge("energy_prices", "inflation", strength=0.6, confidence=0.9, lag=0.0))
    g.add_edge(Edge("energy_prices", "manufacturing", strength=-0.3, confidence=0.8, lag=0.0))
    g.add_edge(Edge("manufacturing", "employment", strength=0.4, confidence=0.8, lag=0.0))
    g.add_edge(Edge("manufacturing", "gdp", strength=0.3, confidence=0.9, lag=0.0))
    g.add_edge(Edge("consumer_spending", "gdp", strength=0.6, confidence=0.9, lag=0.0))
    g.add_edge(Edge("employment", "consumer_spending", strength=0.5, confidence=0.8, lag=0.0))
    g.add_edge(Edge("inflation", "interest_rate", strength=0.5, confidence=0.7, lag=1.0))

    return g

if __name__ == "__main__":
    g = build_graph()
    manager = StateManager()
    manager.base_graph = g
    
    # Scenario A: Oil Shock
    scenario_a = manager.create_scenario("Oil Shock (+30%)")
    engine_a = SimulationEngine(scenario_a)
    engine_a.inject_shock("oil_prices", 0.30)
    
    # Scenario B: Interest Rate Shock
    scenario_b = manager.create_scenario("Interest Rate Shock (+30%)")
    engine_b = SimulationEngine(scenario_b)
    engine_b.inject_shock("interest_rate", 0.30)
    
    exp_engine = ExplainabilityEngine(scenario_a)
    trace = exp_engine.explain("gdp")
    
    print("=== NARRATIVE ===")
    print(trace.summary)
    
    print("\n=== CAUSAL PATH ===")
    for step in trace.causal_chain:
        print(f"{step['from']} -> {step['to']}")
        
    print("\n=== IMPACT ATTRIBUTION (GDP) ===")
    for c in trace.impact_attribution["gdp"]:
        print(f"{c['cause']}: {c['pct_contribution']:.1f}%")

    print("\n")
    print(ScenarioComparisonEngine.compare(scenario_a, scenario_b, ["gdp", "manufacturing", "employment"]))
