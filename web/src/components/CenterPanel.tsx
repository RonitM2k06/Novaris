'use client';

import React from 'react';
import { useWorkspaceStore } from '../store/workspace';
import { X } from 'lucide-react';
import { clsx } from 'clsx';
import ScenarioStudio from './workspace/ScenarioStudio';
import HistoricalReplay from './workspace/HistoricalReplay';
import OntologyExplorer from './workspace/OntologyExplorer';
import ResearchReports from './workspace/ResearchReports';

export default function CenterPanel() {
  const { tabs, activeTabId, setActiveTab, closeTab } = useWorkspaceStore();

  if (tabs.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[var(--color-background)]">
        <div className="text-[var(--color-secondary-text)] opacity-50 select-none pointer-events-none flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-dashed border-[var(--color-secondary-text)] rounded-full animate-spin-slow" />
          <p className="text-xl font-mono tracking-widest">NOVARIS KERNEL IDLE</p>
        </div>
      </div>
    );
  }

  const activeTab = tabs.find(t => t.id === activeTabId);

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-[var(--color-background)]">
      {/* Tab Bar */}
      <div className="flex overflow-x-auto bg-[var(--color-panel)] shrink-0 border-b border-[var(--color-edge)]">
        {tabs.map((tab) => {
          const isActive = tab.id === activeTabId;
          return (
            <div
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'group flex items-center h-9 px-4 min-w-[140px] max-w-[200px] border-r border-[var(--color-edge)] cursor-pointer select-none transition-colors',
                isActive ? 'bg-[var(--color-background)] border-t border-t-[var(--color-accent)]' : 'hover:bg-[var(--color-edge)] bg-[var(--color-panel)] text-[var(--color-secondary-text)] border-t border-t-transparent'
              )}
            >
              <span className="truncate text-xs font-medium flex-1">{tab.title}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  closeTab(tab.id);
                }}
                className={clsx(
                  'ml-2 p-0.5 rounded hover:bg-[var(--color-edge)] opacity-0 group-hover:opacity-100 transition-opacity',
                  isActive && 'opacity-100 text-[var(--color-secondary-text)] hover:text-white'
                )}
              >
                <X size={14} />
              </button>
            </div>
          );
        })}
      </div>

      {/* Tab Content Area */}
      <div className="flex-1 overflow-hidden relative">
        {activeTab?.type === 'ScenarioStudio' && <ScenarioStudio />}
        {activeTab?.type === 'HistoricalReplay' && <HistoricalReplay />}
        {activeTab?.type === 'OntologyExplorer' && <OntologyExplorer />}
        {activeTab?.type === 'ResearchReports' && <ResearchReports />}
        {activeTab?.type === 'CalibrationLab' && (
          <div className="p-8 text-[var(--color-secondary-text)]">Calibration Lab: Under Maintenance.</div>
        )}
      </div>
    </div>
  );
}
