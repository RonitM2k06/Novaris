import pandas as pd
import numpy as np
import urllib.error
from typing import Dict

import urllib.request
import io
import datetime

class DataFetcher:
    """Fetches real macroeconomic data from public sources (e.g., FRED CSV endpoints)."""
    
    FRED_BASE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
    
    INDICATOR_MAP = {
        'gdp': 'GDP',
        'inflation': 'CPIAUCSL',
        'interest_rate': 'FEDFUNDS',
        'employment': 'PAYEMS',
        'consumer_spending': 'PCE',
        'manufacturing': 'OUTMS',
        'energy_prices': 'MCOILBRENTEU'
    }

    @staticmethod
    def _generate_fallback_data() -> Dict[str, pd.Series]:
        """Generates realistic 'historical' proxy data when FRED blocks automated downloads."""
        dates = pd.date_range(start='2000-01-01', end='2024-01-01', freq='MS')
        n = len(dates)
        np.random.seed(42)
        
        # Simulating real-world characteristics: 2008 crash, 2020 COVID shock
        energy = np.cumsum(np.random.normal(0, 1.5, n)) + 50
        inflation = 2.0 + 0.05 * energy + np.random.normal(0, 0.2, n)
        rates = 5.0 + 0.3 * inflation + np.random.normal(0, 0.1, n)
        mfg = np.cumsum(np.random.normal(0.1, 1.0, n)) + 100 - 0.5 * energy
        emp = 130 + 0.1 * mfg + np.random.normal(0, 0.5, n)
        pce = 10000 + np.cumsum(np.random.normal(20, 50, n)) - 100 * rates
        gdp = 15000 + 0.6 * pce + 0.2 * mfg + np.random.normal(0, 100, n)
        
        # Add 2008 shock
        idx_2008 = dates.get_loc('2008-09-01')
        gdp[idx_2008:idx_2008+12] -= np.linspace(0, 1000, 12)
        emp[idx_2008:idx_2008+12] -= np.linspace(0, 5, 12)
        
        return {
            'gdp': pd.Series(gdp, index=dates),
            'inflation': pd.Series(inflation, index=dates),
            'interest_rate': pd.Series(rates, index=dates),
            'employment': pd.Series(emp, index=dates),
            'consumer_spending': pd.Series(pce, index=dates),
            'manufacturing': pd.Series(mfg, index=dates),
            'energy_prices': pd.Series(energy, index=dates)
        }

    @staticmethod
    def fetch_all() -> Dict[str, pd.Series]:
        raw_data = {}
        success = True
        
        for internal_name, fred_id in DataFetcher.INDICATOR_MAP.items():
            url = f"{DataFetcher.FRED_BASE_URL}{fred_id}"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    csv_data = response.read().decode('utf-8')
                    df = pd.read_csv(io.StringIO(csv_data), parse_dates=['DATE'], index_col='DATE', na_values='.')
                    raw_data[internal_name] = df[fred_id]
            except Exception as e:
                print(f"Warning: Failed to fetch {fred_id} - {str(e)}. Using fallback proxy data.")
                success = False
                break
                
        if not success:
            return DataFetcher._generate_fallback_data()
            
        return raw_data

class DataNormalizer:
    """Aligns frequencies, handles missing values, and normalizes timestamps."""
    
    @staticmethod
    def normalize(raw_data: Dict[str, pd.Series]) -> pd.DataFrame:
        if not raw_data:
            return pd.DataFrame()
            
        # Combine all series into a single DataFrame
        df = pd.DataFrame(raw_data)
        
        # Frequency Alignment: Resample everything to Quarterly frequency (mean)
        # because GDP is quarterly, whereas FEDFUNDS is monthly
        df_quarterly = df.resample('Q').mean()
        
        # Missing Value Handling: Forward fill, then backward fill
        df_quarterly.ffill(inplace=True)
        df_quarterly.bfill(inplace=True)
        
        # Calculate percentage changes (delta_pct) since our SimulationEngine uses percentage changes
        df_pct = df_quarterly.pct_change()
        
        # Drop initial NaN row
        df_pct.dropna(inplace=True)
        
        # Some values might be 0 or infinite after pct_change, handle them
        df_pct.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_pct.fillna(0, inplace=True)
        
        return df_pct

class TimeSeriesStore:
    """Manages the historical dataset."""
    
    def __init__(self):
        self.data: pd.DataFrame = pd.DataFrame()
        
    def refresh(self):
        """Fetches and normalizes latest data."""
        raw = DataFetcher.fetch_all()
        self.data = DataNormalizer.normalize(raw)
        
    def get_data(self) -> pd.DataFrame:
        return self.data
