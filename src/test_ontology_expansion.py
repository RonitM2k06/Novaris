from novaris.graph import EconomicGraph, Node, Edge
from novaris.historical_replay import HistoricalScenario, ExpectedOutcome, HistoricalReplayEngine
from test_historical_replay import build_calibrated_graph, build_scenario_library

def build_expanded_graph() -> EconomicGraph:
    g = build_calibrated_graph() 
    
    # Financial System Nodes
    g.add_node(Node("credit_markets", "Credit Markets", 100.0, category="Financial System"))
    g.add_node(Node("housing_markets", "Housing Markets", 100.0, category="Financial System"))
    g.add_node(Node("financial_markets", "Financial Markets", 100.0, category="Financial System"))
    g.add_node(Node("bank_lending", "Bank Lending", 100.0, category="Financial System"))
    g.add_node(Node("corporate_debt", "Corporate Debt", 100.0, category="Financial System"))
    g.add_node(Node("household_debt", "Household Debt", 100.0, category="Financial System"))
    
    # Policy System Nodes
    g.add_node(Node("government_intervention", "Government Intervention", 100.0, category="Policy System"))
    g.add_node(Node("government_subsidies", "Government Subsidies", 100.0, category="Policy System"))
    
    # Behavioral System Nodes
    g.add_node(Node("consumer_confidence", "Consumer Confidence", 100.0, category="Behavioral System"))
    
    # New Relationships
    g.add_edge(Edge("credit_markets", "consumer_spending", strength=0.5, confidence=0.9, lag=0.0))
    g.add_edge(Edge("credit_markets", "housing_markets", strength=0.7, confidence=0.9, lag=0.0))
    g.add_edge(Edge("housing_markets", "consumer_confidence", strength=0.6, confidence=0.8, lag=0.0))
    g.add_edge(Edge("consumer_confidence", "consumer_spending", strength=0.8, confidence=0.9, lag=0.0))
    g.add_edge(Edge("government_intervention", "inflation", strength=0.5, confidence=0.8, lag=1.0))
    g.add_edge(Edge("government_intervention", "employment", strength=0.4, confidence=0.8, lag=1.0))
    g.add_edge(Edge("government_subsidies", "energy_prices", strength=-0.7, confidence=0.9, lag=0.0))
    g.add_edge(Edge("financial_markets", "consumer_confidence", strength=0.5, confidence=0.8, lag=0.0))
    
    # Link missing demand-pull deflation for 2008 fix
    g.add_edge(Edge("consumer_spending", "inflation", strength=0.4, confidence=0.8, lag=1.0))
    g.add_edge(Edge("credit_markets", "inflation", strength=0.3, confidence=0.8, lag=1.0))
    
    return g

def build_expanded_scenarios() -> list[HistoricalScenario]:
    return [
        HistoricalScenario(
            name="2008 Financial Crisis",
            year="2008",
            description="Credit market freeze and housing collapse.",
            initial_shocks={"housing_markets": -0.30, "credit_markets": -0.40},
            expected_outcomes=[
                ExpectedOutcome("gdp", -0.04),
                ExpectedOutcome("inflation", -0.02)
            ]
        ),
        HistoricalScenario(
            name="COVID-19 Economic Shock",
            year="2020",
            description="Lockdown with massive government intervention.",
            initial_shocks={"manufacturing": -0.15, "employment": -0.10, "government_intervention": +0.50},
            expected_outcomes=[
                ExpectedOutcome("gdp", -0.09),
                ExpectedOutcome("consumer_spending", -0.08)
            ]
        ),
        HistoricalScenario(
            name="2022 Energy Crisis",
            year="2022",
            description="Energy spike with government subsidies to cap costs.",
            initial_shocks={"oil_prices": +0.80, "government_subsidies": +0.60},
            expected_outcomes=[
                ExpectedOutcome("inflation", +0.08),
                ExpectedOutcome("manufacturing", -0.05),
                ExpectedOutcome("gdp", -0.02)
            ]
        )
    ]

if __name__ == "__main__":
    old_graph = build_calibrated_graph()
    new_graph = build_expanded_graph()
    
    old_engine = HistoricalReplayEngine(old_graph)
    new_engine = HistoricalReplayEngine(new_graph)
    
    # Use the old shocks for old engine, and expanded shocks for new engine
    # Wait, for a fair comparison of "accuracy" we should just use the best shocks available to each ontology.
    # We'll use old scenarios from Phase 5 for Old Engine
    old_scenarios = {s.name: s for s in build_scenario_library()}
    new_scenarios = {s.name: s for s in build_expanded_scenarios()}
    
    print("=== ONTOLOGY EXPANSION VALIDATION ===")
    
    targets = ["2008 Financial Crisis", "COVID-19 Economic Shock", "2022 Energy Crisis"]
    
    for t in targets:
        print(f"\n--- {t} ---")
        old_res = old_engine.replay(old_scenarios[t])
        new_res = new_engine.replay(new_scenarios[t])
        
        print(f"OLD Agreement Score: {old_res['metrics']['agreement_score']:.1f}/100")
        for exp in old_scenarios[t].expected_outcomes:
            sim_val = old_res['simulated_outcomes'].get(exp.node_id, 0.0)
            print(f"  Old {exp.node_id}: Expected {exp.expected_pct_change*100:+.2f}% | Simulated {sim_val*100:+.2f}%")
            
        print(f"NEW Agreement Score: {new_res['metrics']['agreement_score']:.1f}/100")
        for exp in new_scenarios[t].expected_outcomes:
            sim_val = new_res['simulated_outcomes'].get(exp.node_id, 0.0)
            print(f"  New {exp.node_id}: Expected {exp.expected_pct_change*100:+.2f}% | Simulated {sim_val*100:+.2f}%")
