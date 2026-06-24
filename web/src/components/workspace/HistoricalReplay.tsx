'use client';

import React, { useEffect, useState } from 'react';
import { useWorkspaceStore } from '../../store/workspace';

const SCENARIO_NAMES = [
  '2008 Financial Crisis',
  'COVID-19 Economic Shock',
  '2022 Energy Crisis',
  '1970s Oil Embargo',
  'Dot-com Crash'
];

export default function HistoricalReplay() {
  const { setContextData } = useWorkspaceStore();
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setContextData({
      'Engine Status': {
        'Core': 'StickySimulationEngine',
        'Elasticity': 'Asymmetric',
        'Expectations': 'Adaptive (EMA)'
      },
      'Dataset': {
        'Source': 'FRED / World Bank',
        'Frequency': 'Quarterly',
        'Years': '1970-2024'
      }
    });

    const fetchScenarios = async () => {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const results = [];
      
      for (const name of SCENARIO_NAMES) {
        try {
          const res = await fetch(`${API_URL}/historical-replay`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_name: name })
          });
          const data = await res.json();
          if (data.metrics) {
            results.push({
              name: data.scenario.name,
              year: data.scenario.year,
              agreement: data.metrics.agreement_score,
              err: data.metrics.magnitude_error,
              dir: data.metrics.direction_accuracy
            });
          }
        } catch (e) {
          // Silent fail on error
        }
      }
      setScenarios(results);
      setLoading(false);
    };
    
    fetchScenarios();
  }, [setContextData]);

  return (
    <div className="flex flex-col h-full p-8 text-[var(--color-primary-text)] overflow-y-auto">
      <h2 className="text-xl font-bold tracking-widest mb-8">HISTORICAL REPLAY LAB</h2>
      
      {loading ? (
        <div className="text-[var(--color-secondary-text)] opacity-50 flex items-center gap-4">
          <div className="w-6 h-6 border-2 border-dashed border-[var(--color-secondary-text)] rounded-full animate-spin" />
          <span>Running Historical Simulations...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {scenarios.map(s => (
            <div key={s.name} className="bg-black/20 border border-[var(--color-edge)] p-6 rounded-lg relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4 opacity-10 font-mono text-6xl font-bold">{s.year}</div>
              
              <h3 className="text-lg font-bold mb-1 relative z-10">{s.name}</h3>
              
              <div className="mt-6 space-y-4 relative z-10">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-[var(--color-secondary-text)]">Agreement Score</span>
                    <span className="text-[var(--color-accent)] font-mono">{s.agreement.toFixed(1)}/100</span>
                  </div>
                  <div className="h-1.5 w-full bg-[var(--color-panel)] rounded-full overflow-hidden">
                    <div className="h-full bg-[var(--color-accent)]" style={{ width: `${s.agreement}%` }} />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                   <div className="bg-[var(--color-panel)] p-3 rounded border border-[var(--color-edge)]">
                     <div className="text-[10px] text-[var(--color-secondary-text)] uppercase mb-1">Magnitude Error</div>
                     <div className="font-mono text-[var(--color-warning)]">{s.err.toFixed(2)} pts</div>
                   </div>
                   <div className="bg-[var(--color-panel)] p-3 rounded border border-[var(--color-edge)]">
                     <div className="text-[10px] text-[var(--color-secondary-text)] uppercase mb-1">Direction Accuracy</div>
                     <div className="font-mono text-[var(--color-growth)]">{s.dir.toFixed(0)}%</div>
                   </div>
                </div>
                
                <button className="text-xs text-[var(--color-policy)] hover:underline mt-2">View Detailed Trace &rarr;</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
