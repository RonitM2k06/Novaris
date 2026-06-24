'use client';

import React from 'react';
import LeftPanel from './LeftPanel';
import CenterPanel from './CenterPanel';
import RightPanel from './RightPanel';
import BottomPanel from './BottomPanel';

export default function CommandCenter() {
  return (
    <div className="flex flex-col h-screen w-screen bg-[var(--color-background)] text-[var(--color-primary-text)] font-sans overflow-hidden">
      
      {/* Top Header */}
      <header className="h-10 border-b border-[var(--color-edge)] bg-[var(--color-panel)] flex items-center px-4 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[var(--color-accent)] animate-pulse" />
          <h1 className="text-sm font-bold tracking-widest text-[var(--color-primary-text)] uppercase">Novaris Command Center</h1>
        </div>
        <div className="ml-auto flex items-center gap-4 text-xs text-[var(--color-secondary-text)]">
          <span>STATUS: ONLINE</span>
          <span>ENGINE: NONLINEAR STICKY</span>
        </div>
      </header>

      {/* Main Grid */}
      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Rail */}
        <LeftPanel />

        {/* Tabbed Workspace */}
        <div className="flex flex-1 flex-col border-x border-[var(--color-edge)] min-w-0">
          <CenterPanel />
        </div>

        {/* Intelligence Rail */}
        <RightPanel />
      </div>

      {/* Event Console */}
      <BottomPanel />
    </div>
  );
}
