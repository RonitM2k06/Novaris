from novaris.graph import EconomicGraph, Node, Edge
from novaris.historical_replay import HistoricalScenario, ExpectedOutcome, HistoricalReplayEngine

def build_calibrated_graph() -> EconomicGraph:
    """Builds the graph using the parameters discovered in Phase 4 Real Data Calibration."""
    g = EconomicGraph()
    g.add_node(Node("interest_rate", "Interest Rate", 5.0, category="Policy"))
    g.add_node(Node("oil_prices", "Oil Prices", 80.0, category="External"))
    g.add_node(Node("manufacturing", "Manufacturing Output", 500.0, category="Sector"))
    g.add_node(Node("consumer_spending", "Consumer Spending", 1000.0, category="Macroeconomic"))
    g.add_node(Node("employment", "Employment", 150.0, category="Macroeconomic"))
    g.add_node(Node("gdp", "GDP", 2000.0, category="Macroeconomic"))
    g.add_node(Node("energy_prices", "Energy Prices", 100.0, category="Macroeconomic"))
    g.add_node(Node("inflation", "Inflation", 3.0, category="Macroeconomic"))

    # Adding generic edges + calibrated parameters
    g.add_edge(Edge("oil_prices", "energy_prices", strength=0.8, confidence=0.9, lag=0.0))
    g.add_edge(Edge("energy_prices", "inflation", strength=0.521, confidence=1.0, lag=0.0))
    g.add_edge(Edge("energy_prices", "manufacturing", strength=-0.652, confidence=1.0, lag=0.0))
    g.add_edge(Edge("manufacturing", "employment", strength=0.309, confidence=0.997, lag=0.0))
    g.add_edge(Edge("manufacturing", "gdp", strength=0.3, confidence=0.9, lag=0.0))
    g.add_edge(Edge("consumer_spending", "gdp", strength=0.321, confidence=0.99, lag=0.0))
    g.add_edge(Edge("inflation", "interest_rate", strength=0.558, confidence=1.0, lag=0.0))
    g.add_edge(Edge("employment", "consumer_spending", strength=0.5, confidence=0.8, lag=0.0))
    # Interest -> Consumer edge removed as per Phase 4 recommendation
    
    return g

def build_scenario_library() -> list[HistoricalScenario]:
    return [
        HistoricalScenario(
            name="2008 Financial Crisis",
            year="2008",
            description="Massive demand destruction and job losses stemming from the housing collapse.",
            initial_shocks={"consumer_spending": -0.10, "employment": -0.05},
            expected_outcomes=[
                ExpectedOutcome("gdp", -0.04),
                ExpectedOutcome("inflation", -0.02)
            ]
        ),
        HistoricalScenario(
            name="COVID-19 Economic Shock",
            year="2020",
            description="Global lockdown forcing immediate manufacturing and employment freezes.",
            initial_shocks={"manufacturing": -0.15, "employment": -0.10},
            expected_outcomes=[
                ExpectedOutcome("gdp", -0.09),
                ExpectedOutcome("consumer_spending", -0.08)
            ]
        ),
        HistoricalScenario(
            name="2022 Energy Crisis",
            year="2022",
            description="Geopolitical shock causing massive spikes in crude oil and natural gas.",
            initial_shocks={"oil_prices": +0.80},
            expected_outcomes=[
                ExpectedOutcome("inflation", +0.08),
                ExpectedOutcome("manufacturing", -0.05),
                ExpectedOutcome("gdp", -0.02)
            ]
        ),
        HistoricalScenario(
            name="Dot-com Crash",
            year="2000",
            description="Burst of the tech bubble causing a mild recession primarily in investment and employment.",
            initial_shocks={"employment": -0.02},
            expected_outcomes=[
                ExpectedOutcome("gdp", -0.005),
                ExpectedOutcome("consumer_spending", -0.01)
            ]
        ),
        HistoricalScenario(
            name="1970s Oil Embargo",
            year="1973",
            description="OPEC embargo causing severe stagflation.",
            initial_shocks={"oil_prices": +1.50},
            expected_outcomes=[
                ExpectedOutcome("inflation", +0.12),
                ExpectedOutcome("gdp", -0.03)
            ]
        )
    ]

if __name__ == "__main__":
    graph = build_calibrated_graph()
    engine = HistoricalReplayEngine(graph)
    library = build_scenario_library()
    
    print("=== HISTORICAL REPLAY VALIDATION ===")
    
    for scenario in library:
        result = engine.replay(scenario)
        metrics = result['metrics']
        print(f"\n--- {scenario.name} ({scenario.year}) ---")
        print(f"Description: {scenario.description}")
        print("Outcomes:")
        for exp in scenario.expected_outcomes:
            sim_val = result['simulated_outcomes'].get(exp.node_id, 0.0)
            print(f"  {exp.node_id}: Expected {exp.expected_pct_change*100:+.2f}% | Simulated {sim_val*100:+.2f}%")
        
        print(f"Direction Accuracy: {metrics['direction_accuracy']:.1f}%")
        print(f"Magnitude Error: {metrics['magnitude_error']:.2f} percentage points")
        print(f"Agreement Score: {metrics['agreement_score']:.1f}/100")
