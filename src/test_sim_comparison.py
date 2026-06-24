import sys
from novaris.graph import EconomicGraph, Node, Edge
from novaris.state import StateManager
from novaris.simulation import SimulationEngine
from novaris.explainability import ScenarioComparisonEngine

def build_graph(calibrated=False) -> EconomicGraph:
    g = EconomicGraph()
    g.add_node(Node("interest_rate", "Interest Rate", 5.0, category="Policy"))
    g.add_node(Node("oil_prices", "Oil Prices", 80.0, category="External"))
    g.add_node(Node("manufacturing", "Manufacturing Output", 500.0, category="Sector"))
    g.add_node(Node("consumer_spending", "Consumer Spending", 1000.0, category="Macroeconomic"))
    g.add_node(Node("employment", "Employment", 150.0, category="Macroeconomic"))
    g.add_node(Node("gdp", "GDP", 2000.0, category="Macroeconomic"))
    g.add_node(Node("energy_prices", "Energy Prices", 100.0, category="Macroeconomic"))
    g.add_node(Node("inflation", "Inflation", 3.0, category="Macroeconomic"))

    # Adding a generic edge to link manufacturing back to GDP so we can see full effects in both
    g.add_edge(Edge("manufacturing", "gdp", strength=0.3, confidence=0.9, lag=0.0))

    if not calibrated:
        g.add_edge(Edge("interest_rate", "consumer_spending", strength=-0.5, confidence=0.9, lag=1.0))
        g.add_edge(Edge("oil_prices", "energy_prices", strength=0.8, confidence=0.9, lag=0.0))
        g.add_edge(Edge("energy_prices", "inflation", strength=0.6, confidence=0.9, lag=0.0))
        g.add_edge(Edge("energy_prices", "manufacturing", strength=-0.3, confidence=0.8, lag=0.0))
        g.add_edge(Edge("manufacturing", "employment", strength=0.4, confidence=0.8, lag=0.0))
        g.add_edge(Edge("consumer_spending", "gdp", strength=0.6, confidence=0.9, lag=0.0))
        g.add_edge(Edge("inflation", "interest_rate", strength=0.5, confidence=0.7, lag=1.0))
    else:
        # Calibrated strengths and lags from real data fallback
        g.add_edge(Edge("interest_rate", "consumer_spending", strength=-0.074, confidence=0.514, lag=3.0))
        g.add_edge(Edge("oil_prices", "energy_prices", strength=0.8, confidence=0.9, lag=0.0))
        g.add_edge(Edge("energy_prices", "inflation", strength=0.521, confidence=1.0, lag=0.0))
        g.add_edge(Edge("energy_prices", "manufacturing", strength=-0.652, confidence=1.0, lag=0.0))
        g.add_edge(Edge("manufacturing", "employment", strength=0.309, confidence=0.997, lag=0.0))
        g.add_edge(Edge("consumer_spending", "gdp", strength=0.321, confidence=0.99, lag=0.0))
        g.add_edge(Edge("inflation", "interest_rate", strength=0.558, confidence=1.0, lag=0.0))

    return g

if __name__ == "__main__":
    manager = StateManager()
    
    # Old Graph
    manager.base_graph = build_graph(calibrated=False)
    scenario_old = manager.create_scenario("Old Graph - Oil Shock (+30%)")
    engine_old = SimulationEngine(scenario_old)
    engine_old.inject_shock("oil_prices", 0.30)
    
    # Calibrated Graph
    manager.base_graph = build_graph(calibrated=True)
    scenario_cal = manager.create_scenario("Calibrated Graph - Oil Shock (+30%)")
    engine_cal = SimulationEngine(scenario_cal)
    engine_cal.inject_shock("oil_prices", 0.30)
    
    print(ScenarioComparisonEngine.compare(scenario_old, scenario_cal, ["gdp", "manufacturing", "inflation", "consumer_spending"]))
