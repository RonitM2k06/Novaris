'use client';

import React from 'react';
import { useWorkspaceStore } from '../store/workspace';

export default function RightPanel() {
  const { activeTabId, contextData } = useWorkspaceStore();

  return (
    <div className="w-64 shrink-0 bg-[var(--color-panel)] border-l border-[var(--color-edge)] flex flex-col p-4 overflow-y-auto">
      <h2 className="text-xs font-bold tracking-widest text-[var(--color-secondary-text)] uppercase mb-4">Intelligence Rail</h2>
      
      {!contextData ? (
        <div className="text-sm text-[var(--color-secondary-text)] opacity-60 italic">
          No context selected.
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(contextData).map(([sectionTitle, dataObj]: [string, any]) => (
            <div key={sectionTitle}>
              <h3 className="text-xs font-semibold text-[var(--color-primary-text)] mb-2 uppercase border-b border-[var(--color-edge)] pb-1">{sectionTitle}</h3>
              <ul className="space-y-1">
                {Object.entries(dataObj).map(([key, val]: [string, any]) => (
                  <li key={key} className="flex justify-between text-xs">
                    <span className="text-[var(--color-secondary-text)]">{key}</span>
                    <span className="font-mono text-[var(--color-accent)]">{val}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
      
      <div className="mt-auto pt-8">
        <div className="h-32 border border-[var(--color-edge)] rounded bg-black/50 p-2 flex flex-col justify-end">
           <div className="w-full h-1/2 bg-gradient-to-t from-[var(--color-accent)]/20 to-transparent" />
           <div className="text-[10px] text-[var(--color-secondary-text)] mt-2">Network Centrality Matrix</div>
        </div>
      </div>
    </div>
  );
}
