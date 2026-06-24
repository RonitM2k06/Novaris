import numpy as np
import pandas as pd
from novaris.graph import EconomicGraph, Node, Edge
from novaris.calibration import CalibrationEngine, GraphUpdateEngine

def generate_mock_historical_data(n_periods=100) -> pd.DataFrame:
    """Generates synthetic time-series data with embedded causal relationships."""
    np.random.seed(42)
    
    # Base trends (random walks with drift)
    time = np.arange(n_periods)
    
    # 1. Energy Prices (Random exogenous shock)
    energy_prices = np.cumsum(np.random.normal(0, 2, n_periods)) + 100
    
    # 2. Inflation (Caused by Energy Prices, lag 0)
    inflation = 3.0 + 0.1 * energy_prices + np.random.normal(0, 0.5, n_periods)
    
    # 3. Interest Rates (Central bank reacts to inflation, lag 1)
    interest_rates = np.zeros(n_periods)
    for t in range(1, n_periods):
        interest_rates[t] = 2.0 + 0.5 * inflation[t-1] + np.random.normal(0, 0.2)
    interest_rates[0] = 5.0
    
    # 4. Consumer Spending (Hurt by Interest Rates, lag 1)
    consumer_spending = np.zeros(n_periods)
    for t in range(1, n_periods):
        consumer_spending[t] = 1000 - 50 * interest_rates[t-1] + np.random.normal(0, 10)
    consumer_spending[0] = 800
    
    # 5. Manufacturing (Hurt by Energy Prices lag 0, Hurt by Interest rates lag 2)
    manufacturing = np.zeros(n_periods)
    for t in range(2, n_periods):
        manufacturing[t] = 500 - 2 * energy_prices[t] - 30 * interest_rates[t-2] + np.random.normal(0, 5)
    manufacturing[:2] = 400
    
    # 6. Employment (Driven by Manufacturing lag 0)
    employment = 50 + 0.2 * manufacturing + np.random.normal(0, 2, n_periods)
    
    # 7. GDP (Driven by Consumer Spending and Manufacturing lag 0)
    gdp = 0.6 * consumer_spending + 0.4 * manufacturing + np.random.normal(0, 20, n_periods)
    
    return pd.DataFrame({
        'interest_rate': interest_rates,
        'energy_prices': energy_prices,
        'inflation': inflation,
        'consumer_spending': consumer_spending,
        'manufacturing': manufacturing,
        'employment': employment,
        'gdp': gdp
    })

def test_calibration():
    # Load Data
    data = generate_mock_historical_data()
    cal_engine = CalibrationEngine(data)
    
    # Define hardcoded edges to test
    edges_to_test = [
        Edge("interest_rate", "consumer_spending", strength=-0.5, confidence=0.9, lag=1.0),
        Edge("energy_prices", "inflation", strength=0.6, confidence=0.9, lag=0.0),
        Edge("energy_prices", "manufacturing", strength=-0.3, confidence=0.8, lag=0.0),
        Edge("manufacturing", "employment", strength=0.4, confidence=0.8, lag=0.0),
        Edge("consumer_spending", "gdp", strength=0.6, confidence=0.9, lag=0.0),
        Edge("inflation", "interest_rate", strength=0.5, confidence=0.7, lag=1.0)
    ]
    
    print("=== CAUSAL CALIBRATION ENGINE ===")
    
    comparisons = []
    for edge in edges_to_test:
        calibrated = cal_engine.calibrate_relationship(edge.source_id, edge.target_id)
        comp = GraphUpdateEngine.compare(edge, calibrated)
        comparisons.append(comp)
        
        print(f"\n{edge.source_id} -> {edge.target_id}")
        print(f"Pearson: {calibrated.pearson:+.3f}")
        print(f"Spearman: {calibrated.spearman:+.3f}")
        print(f"Best Lag: {calibrated.best_lag} quarters")
        print(f"Confidence: {calibrated.confidence:.3f}")
        print(f"Suggested Edge Strength: {calibrated.suggested_strength:+.3f}")
        print(f"--- UPDATE ENGINE ---")
        print(f"Current Strength: {edge.strength:+.3f}")
        print(f"Difference: {comp['difference']:.3f}")

if __name__ == "__main__":
    test_calibration()
