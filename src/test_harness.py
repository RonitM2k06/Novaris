import sys
from novaris.graph import EconomicGraph, Node, Edge
from novaris.state import StateManager
from novaris.simulation import SimulationEngine

def build_graph() -> EconomicGraph:
    g = EconomicGraph()
    # Nodes
    # Policy
    g.add_node(Node("interest_rate", "Interest Rate", 5.0, category="Policy"))
    g.add_node(Node("gov_spending", "Government Spending", 100.0, category="Policy"))
    
    # External
    g.add_node(Node("oil_prices", "Oil Prices", 80.0, category="External"))
    g.add_node(Node("exports", "Exports", 200.0, category="External"))
    
    # Sector
    g.add_node(Node("manufacturing", "Manufacturing Output", 500.0, category="Sector"))
    g.add_node(Node("services", "Services Output", 800.0, category="Sector"))
    g.add_node(Node("agriculture", "Agriculture Output", 100.0, category="Sector"))
    
    # Macroeconomic
    g.add_node(Node("consumer_spending", "Consumer Spending", 1000.0, category="Macroeconomic"))
    g.add_node(Node("inflation", "Inflation", 3.0, category="Macroeconomic"))
    g.add_node(Node("employment", "Employment", 150.0, category="Macroeconomic"))
    g.add_node(Node("gdp", "GDP", 2000.0, category="Macroeconomic"))
    g.add_node(Node("currency_value", "Currency Value", 100.0, category="Macroeconomic"))
    g.add_node(Node("energy_prices", "Energy Prices", 100.0, category="Macroeconomic"))

    # Edges
    # Policy -> Macro/Sector
    g.add_edge(Edge("interest_rate", "consumer_spending", strength=-0.5, confidence=0.9, lag=1.0))
    g.add_edge(Edge("interest_rate", "manufacturing", strength=-0.4, confidence=0.8, lag=2.0))
    g.add_edge(Edge("interest_rate", "currency_value", strength=0.4, confidence=0.7, lag=0.0))
    g.add_edge(Edge("gov_spending", "employment", strength=0.3, confidence=0.7, lag=1.0))
    g.add_edge(Edge("gov_spending", "gdp", strength=0.5, confidence=0.8, lag=1.0))
    
    # External -> Macro/Sector
    g.add_edge(Edge("oil_prices", "energy_prices", strength=0.8, confidence=0.9, lag=0.0))
    g.add_edge(Edge("exports", "manufacturing", strength=0.6, confidence=0.8, lag=1.0))
    g.add_edge(Edge("exports", "gdp", strength=0.4, confidence=0.9, lag=1.0))
    
    # Macro -> External
    g.add_edge(Edge("currency_value", "exports", strength=-0.5, confidence=0.8, lag=1.0))

    # Sector -> Macro
    g.add_edge(Edge("manufacturing", "employment", strength=0.4, confidence=0.8, lag=0.0))
    g.add_edge(Edge("services", "employment", strength=0.5, confidence=0.8, lag=0.0))
    g.add_edge(Edge("manufacturing", "gdp", strength=0.3, confidence=0.9, lag=0.0))
    g.add_edge(Edge("services", "gdp", strength=0.5, confidence=0.9, lag=0.0))
    
    # Macro -> Macro
    g.add_edge(Edge("consumer_spending", "gdp", strength=0.6, confidence=0.9, lag=0.0))
    g.add_edge(Edge("consumer_spending", "inflation", strength=0.4, confidence=0.7, lag=1.0))
    g.add_edge(Edge("energy_prices", "inflation", strength=0.6, confidence=0.9, lag=0.0))
    g.add_edge(Edge("energy_prices", "manufacturing", strength=-0.3, confidence=0.8, lag=0.0))
    g.add_edge(Edge("inflation", "interest_rate", strength=0.5, confidence=0.7, lag=1.0)) 
    g.add_edge(Edge("employment", "consumer_spending", strength=0.5, confidence=0.8, lag=0.0))

    return g

def run_scenario(g, name, shock_node, shock_pct):
    manager = StateManager()
    manager.base_graph = g
    scenario = manager.create_scenario(name)
    engine = SimulationEngine(scenario)
    engine.inject_shock(shock_node, shock_pct)
    
    print(f"\n{'='*50}\nSCENARIO: {name}\n{'='*50}")
    history_by_step = {}
    for entry in scenario.history:
        ts = entry['time_step']
        if ts not in history_by_step:
            history_by_step[ts] = []
        history_by_step[ts].append(entry)
        
    for ts in sorted(history_by_step.keys()):
        print(f"\n[Time Step {ts}]")
        for entry in history_by_step[ts]:
            node_id = entry['node_id']
            pct = entry['delta_pct'] * 100
            cause = entry['cause_id']
            print(f"  -> {node_id}: {pct:+.2f}% (Caused by: {cause})")

if __name__ == "__main__":
    g = build_graph()
    run_scenario(g, "Interest Rate +40% (e.g. from 5% to 7%)", "interest_rate", 0.40)
    run_scenario(g, "Interest Rate -40% (e.g. from 5% to 3%)", "interest_rate", -0.40)
    run_scenario(g, "Oil Prices +30%", "oil_prices", 0.30)
    run_scenario(g, "Oil Prices -20%", "oil_prices", -0.20)
    run_scenario(g, "Government Spending +15%", "gov_spending", 0.15)
    run_scenario(g, "Export Shock -25%", "exports", -0.25)
    run_scenario(g, "Energy Crisis (+50% energy)", "energy_prices", 0.50)
    run_scenario(g, "Currency Devaluation (-15%)", "currency_value", -0.15)
    run_scenario(g, "Inflation Spike (+30%)", "inflation", 0.30)
    run_scenario(g, "Employment Collapse (-10%)", "employment", -0.10)
