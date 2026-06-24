import numpy as np
import pandas as pd
from typing import Dict, Any, List
from dataclasses import dataclass
from scipy.stats import pearsonr, spearmanr

@dataclass
class CalibratedEdge:
    source: str
    target: str
    pearson: float
    spearman: float
    best_lag: int
    confidence: float
    suggested_strength: float

class CalibrationEngine:
    """Calibrates graph edges based on historical economic time-series data."""
    
    def __init__(self, data: pd.DataFrame):
        """
        data: DataFrame where rows are time-steps (e.g., quarters) 
              and columns are node IDs (e.g., 'gdp', 'inflation').
        """
        self.data = data
        
    def _cross_correlation_lag(self, x: np.ndarray, y: np.ndarray, max_lag: int = 4) -> int:
        """Finds the lag that maximizes the absolute cross-correlation."""
        best_lag = 0
        max_corr = 0
        
        # We test how x (source) at t-lag predicts y (target) at t
        for lag in range(max_lag + 1):
            if lag == 0:
                corr = np.corrcoef(x, y)[0, 1]
            else:
                corr = np.corrcoef(x[:-lag], y[lag:])[0, 1]
                
            if not np.isnan(corr) and abs(corr) > abs(max_corr):
                max_corr = corr
                best_lag = lag
                
        return best_lag
        
    def calibrate_relationship(self, source: str, target: str) -> CalibratedEdge:
        """Calculates statistical metrics between a source and target."""
        if source not in self.data.columns or target not in self.data.columns:
            raise ValueError(f"Missing data for {source} or {target}")
            
        x = self.data[source].values
        y = self.data[target].values
        
        # Pearson and Spearman
        p_corr, p_pval = pearsonr(x, y)
        s_corr, s_pval = spearmanr(x, y)
        
        # Best Lag (up to 4 quarters)
        best_lag = self._cross_correlation_lag(x, y, max_lag=4)
        
        # Granger Causality placeholder (using p-value from correlation as a proxy for confidence for now)
        # Real implementation would use statsmodels.tsa.stattools.grangercausalitytests
        confidence = 1.0 - p_pval
        if confidence < 0: confidence = 0.0
        
        # Suggested strength: Since these are normalized % changes, correlation is a good proxy for strength
        # We can blend Pearson and Spearman
        suggested_strength = (p_corr + s_corr) / 2.0
        
        return CalibratedEdge(
            source=source,
            target=target,
            pearson=p_corr,
            spearman=s_corr,
            best_lag=best_lag,
            confidence=confidence,
            suggested_strength=suggested_strength
        )

class GraphUpdateEngine:
    """Compares current hardcoded edges against calibrated edges."""
    
    @staticmethod
    def compare(current_edge, calibrated_edge: CalibratedEdge) -> Dict[str, Any]:
        """Calculates the difference between the expert heuristic and data reality."""
        strength_diff = abs(current_edge.strength - calibrated_edge.suggested_strength)
        
        return {
            'source': current_edge.source_id,
            'target': current_edge.target_id,
            'current_strength': current_edge.strength,
            'calibrated_strength': calibrated_edge.suggested_strength,
            'difference': strength_diff,
            'current_lag': current_edge.lag,
            'calibrated_lag': calibrated_edge.best_lag,
            'calibrated_confidence': calibrated_edge.confidence
        }
