'use client';

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '../../store/workspace';
import { Play } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function ScenarioStudio() {
  const { addLog, setContextData } = useWorkspaceStore();
  const [running, setRunning] = useState(false);
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    setContextData({
      'Scenario Parameters': {
        Shock: '+30%',
        Target: 'Oil Prices',
        Engine: 'Nonlinear Sticky'
      },
      'Calibration Source': {
        'Confidence': '0.99',
        'Data': 'FRED Historical'
      }
    });
  }, [setContextData]);

  const runSimulation = async () => {
    setRunning(true);
    addLog({ type: 'INFO', message: 'Initiating Simulation: Oil Shock +30%' });
    
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ shocks: { 'oil_prices': 0.3 }, duration: 4 })
      });
      const result = await response.json();
      
      const gdpOutcome = (result.outcomes['gdp'] * 100).toFixed(2);
      const infOutcome = (result.outcomes['inflation'] * 100).toFixed(2);
      const mfgOutcome = (result.outcomes['manufacturing'] * 100).toFixed(2);
      
      addLog({ type: 'CASCADE', message: `Manufacturing Output impact: ${mfgOutcome}%` });
      addLog({ type: 'RESULT', message: `GDP Impact: ${gdpOutcome}%` });
      addLog({ type: 'RESULT', message: `Inflation Impact: +${infOutcome}%` });
      
      // Transform history for recharts
      let mockData = [
        { quarter: 'Q1', gdp: 0, inflation: 0, manufacturing: 0 },
        { quarter: 'Q2', gdp: parseFloat(gdpOutcome) * 0.2, inflation: parseFloat(infOutcome) * 0.2, manufacturing: parseFloat(mfgOutcome) * 0.2 },
        { quarter: 'Q3', gdp: parseFloat(gdpOutcome) * 0.7, inflation: parseFloat(infOutcome) * 0.7, manufacturing: parseFloat(mfgOutcome) * 0.7 },
        { quarter: 'Q4', gdp: parseFloat(gdpOutcome), inflation: parseFloat(infOutcome), manufacturing: parseFloat(mfgOutcome) }
      ];
      setData(mockData);
    } catch (e) {
      addLog({ type: 'WARNING', message: 'Failed to connect to backend engine.' });
    }
    
    setRunning(false);
  };

  return (
    <div className="flex flex-col h-full p-8 text-[var(--color-primary-text)]">
      <h2 className="text-xl font-bold tracking-widest mb-8">SCENARIO STUDIO</h2>
      
      <div className="flex gap-8">
        <div className="w-1/3 bg-black/20 border border-[var(--color-edge)] p-6 rounded-lg">
          <h3 className="text-sm font-semibold text-[var(--color-secondary-text)] uppercase mb-4">Input Parameters</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-xs mb-1 text-[var(--color-secondary-text)]">Target Node</label>
              <select className="w-full bg-[var(--color-panel)] border border-[var(--color-edge)] rounded p-2 text-sm focus:border-[var(--color-accent)] outline-none">
                <option>Oil Prices</option>
                <option>Interest Rates</option>
                <option>Government Subsidies</option>
              </select>
            </div>
            <div>
              <label className="block text-xs mb-1 text-[var(--color-secondary-text)]">Magnitude (%)</label>
              <input type="number" defaultValue={30} className="w-full bg-[var(--color-panel)] border border-[var(--color-edge)] rounded p-2 text-sm focus:border-[var(--color-accent)] outline-none" />
            </div>
            <div>
              <label className="block text-xs mb-1 text-[var(--color-secondary-text)]">Duration (Quarters)</label>
              <input type="number" defaultValue={4} className="w-full bg-[var(--color-panel)] border border-[var(--color-edge)] rounded p-2 text-sm focus:border-[var(--color-accent)] outline-none" />
            </div>
            
            <button 
              onClick={runSimulation}
              disabled={running}
              className="w-full mt-4 bg-[var(--color-accent)]/10 hover:bg-[var(--color-accent)]/20 text-[var(--color-accent)] border border-[var(--color-accent)]/50 font-bold py-2 px-4 rounded transition-colors flex items-center justify-center gap-2"
            >
              <Play size={16} />
              {running ? 'COMPUTING...' : 'RUN SIMULATION'}
            </button>
          </div>
        </div>
        
        <div className="flex-1 bg-black/20 border border-[var(--color-edge)] p-6 rounded-lg flex flex-col">
          <h3 className="text-sm font-semibold text-[var(--color-secondary-text)] uppercase mb-4">Simulation Trajectory</h3>
          
          <div className="flex-1 min-h-[300px]">
            {data.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-edge)" />
                  <XAxis dataKey="quarter" stroke="var(--color-secondary-text)" fontSize={12} />
                  <YAxis stroke="var(--color-secondary-text)" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--color-panel)', borderColor: 'var(--color-edge)', color: 'var(--color-primary-text)' }}
                  />
                  <Line type="monotone" dataKey="gdp" stroke="var(--color-warning)" strokeWidth={2} name="GDP %" />
                  <Line type="monotone" dataKey="inflation" stroke="var(--color-inflation)" strokeWidth={2} name="Inflation %" />
                  <Line type="monotone" dataKey="manufacturing" stroke="var(--color-policy)" strokeWidth={2} name="Mfg %" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="w-full h-full flex items-center justify-center text-[var(--color-secondary-text)] opacity-50">
                Awaiting parameters...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
