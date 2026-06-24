'use client';

import React from 'react';
import { useWorkspaceStore } from '../store/workspace';
import { Activity, History, Network, FileText, Beaker } from 'lucide-react';
import { clsx } from 'clsx';

const NAV_ITEMS = [
  { id: 'scenario-studio', type: 'ScenarioStudio', label: 'Scenario Studio', icon: Activity },
  { id: 'historical-replay', type: 'HistoricalReplay', label: 'Historical Replay', icon: History },
  { id: 'ontology-explorer', type: 'OntologyExplorer', label: 'Ontology Explorer', icon: Network },
  { id: 'calibration-lab', type: 'CalibrationLab', label: 'Calibration Lab', icon: Beaker },
  { id: 'research-reports', type: 'ResearchReports', label: 'Research Reports', icon: FileText }
] as const;

export default function LeftPanel() {
  const { openTab, activeTabId } = useWorkspaceStore();

  return (
    <div className="w-14 shrink-0 bg-[var(--color-panel)] flex flex-col items-center py-4 gap-4">
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon;
        const isActive = activeTabId === item.id;
        
        return (
          <button
            key={item.id}
            title={item.label}
            onClick={() => openTab({ id: item.id, type: item.type, title: item.label })}
            className={clsx(
              'p-2 rounded-lg transition-colors group relative flex items-center justify-center',
              isActive ? 'text-[var(--color-accent)]' : 'text-[var(--color-secondary-text)] hover:text-[var(--color-primary-text)] hover:bg-[var(--color-edge)]'
            )}
          >
            <Icon size={22} strokeWidth={isActive ? 2.5 : 1.5} />
            {isActive && (
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-[var(--color-accent)] rounded-r-full -ml-3" />
            )}
          </button>
        );
      })}
    </div>
  );
}
