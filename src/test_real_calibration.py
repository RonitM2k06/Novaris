import pandas as pd
from novaris.data import TimeSeriesStore
from novaris.calibration import CalibrationEngine, GraphUpdateEngine
from novaris.graph import Edge

def run_real_calibration():
    print("Fetching and normalizing real data from FRED...")
    store = TimeSeriesStore()
    store.refresh()
    
    data = store.get_data()
    if data.empty:
        print("Failed to download or parse data.")
        return
        
    print(f"Successfully loaded real data from {data.index.min().date()} to {data.index.max().date()} ({len(data)} quarters)")
    
    cal_engine = CalibrationEngine(data)
    
    edges_to_test = [
        Edge("interest_rate", "consumer_spending", strength=-0.5, confidence=0.9, lag=1.0),
        Edge("energy_prices", "inflation", strength=0.6, confidence=0.9, lag=0.0),
        Edge("energy_prices", "manufacturing", strength=-0.3, confidence=0.8, lag=0.0),
        Edge("manufacturing", "employment", strength=0.4, confidence=0.8, lag=0.0),
        Edge("consumer_spending", "gdp", strength=0.6, confidence=0.9, lag=0.0),
        Edge("inflation", "interest_rate", strength=0.5, confidence=0.7, lag=1.0)
    ]
    
    print("\n=== REAL WORLD CALIBRATION RESULTS ===")
    for edge in edges_to_test:
        try:
            calibrated = cal_engine.calibrate_relationship(edge.source_id, edge.target_id)
            comp = GraphUpdateEngine.compare(edge, calibrated)
            
            print(f"\n{edge.source_id} -> {edge.target_id}")
            print(f"Pearson: {calibrated.pearson:+.3f}")
            print(f"Spearman: {calibrated.spearman:+.3f}")
            print(f"Best Lag: {calibrated.best_lag} quarters")
            print(f"Confidence: {calibrated.confidence:.3f}")
            print(f"Suggested Edge Strength: {calibrated.suggested_strength:+.3f}")
            print(f"--- UPDATE ENGINE ---")
            print(f"Current Strength: {edge.strength:+.3f}")
            print(f"Difference: {comp['difference']:.3f}")
        except Exception as e:
            print(f"\nFailed to calibrate {edge.source_id} -> {edge.target_id}: {e}")

if __name__ == "__main__":
    run_real_calibration()
