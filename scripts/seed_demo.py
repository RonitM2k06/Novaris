import pandas as pd
import numpy as np
import os
import sqlite3

def generate_demo_data():
    """Generates synthetic macroeconomic proxy data for fresh GitHub clones."""
    
    print("Initializing Novaris Demo Dataset Generator...")
    
    # Create quarters from 2000-Q1 to 2024-Q4
    dates = pd.date_range(start='2000-01-01', end='2024-12-31', freq='QE')
    
    df = pd.DataFrame({'date': dates})
    
    # Base Trends
    df['gdp'] = 10000 + np.cumsum(np.random.normal(50, 20, len(dates)))
    df['inflation'] = 2.0 + np.random.normal(0, 0.5, len(dates))
    df['employment'] = 95.0 + np.random.normal(0, 1.0, len(dates))
    df['energy_prices'] = 60 + np.cumsum(np.random.normal(0, 2, len(dates)))
    
    # Inject 2008 Crisis
    idx_2008 = df[df['date'].dt.year == 2008].index
    if not idx_2008.empty:
        start_idx = idx_2008[0]
        df.loc[start_idx:start_idx+4, 'gdp'] *= np.linspace(1, 0.95, 5)
        df.loc[start_idx:start_idx+4, 'employment'] -= np.linspace(0, 4.0, 5)
        df.loc[start_idx:start_idx+4, 'inflation'] -= np.linspace(0, 3.5, 5)

    # Inject COVID Shock
    idx_2020 = df[df['date'].dt.year == 2020].index
    if not idx_2020.empty:
        start_idx = idx_2020[0]
        df.loc[start_idx:start_idx+2, 'gdp'] *= np.array([0.90, 0.85, 0.95][:len(df.loc[start_idx:start_idx+2])])
        df.loc[start_idx:start_idx+2, 'employment'] -= np.array([8.0, 10.0, 5.0][:len(df.loc[start_idx:start_idx+2])])

    # Inject 2022 Energy Crisis
    idx_2022 = df[df['date'].dt.year == 2022].index
    if not idx_2022.empty:
        start_idx = idx_2022[0]
        df.loc[start_idx:start_idx+3, 'energy_prices'] *= np.array([1.5, 2.0, 2.2, 1.8][:len(df.loc[start_idx:start_idx+3])])
        df.loc[start_idx:start_idx+3, 'inflation'] += np.array([2.0, 4.0, 5.5, 3.0][:len(df.loc[start_idx:start_idx+3])])

    # Save to SQLite and CSV
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    csv_path = os.path.join(data_dir, 'macro_demo.csv')
    df.to_csv(csv_path, index=False)
    print(f"[SUCCESS] Wrote {len(df)} records to {csv_path}")
    
    db_path = os.path.join(data_dir, 'novaris.db')
    conn = sqlite3.connect(db_path)
    df.to_sql('macro_timeseries', conn, if_exists='replace', index=False)
    conn.close()
    print(f"[SUCCESS] Populated SQLite database at {db_path}")

if __name__ == "__main__":
    generate_demo_data()
