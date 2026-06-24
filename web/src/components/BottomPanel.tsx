'use client';

import React, { useRef, useEffect } from 'react';
import { useWorkspaceStore } from '../store/workspace';
import { Terminal } from 'lucide-react';
import { clsx } from 'clsx';

export default function BottomPanel() {
  const { logs, clearLogs } = useWorkspaceStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  return (
    <div className="h-48 shrink-0 bg-[var(--color-panel)] border-t border-[var(--color-edge)] flex flex-col">
      <div className="h-8 flex items-center px-4 border-b border-[var(--color-edge)] justify-between bg-black/20">
        <div className="flex items-center gap-2 text-xs text-[var(--color-secondary-text)] uppercase font-semibold">
          <Terminal size={14} />
          <span>Event Console</span>
        </div>
        <button onClick={clearLogs} className="text-xs text-[var(--color-secondary-text)] hover:text-white">
          Clear
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2 font-mono text-xs space-y-1">
        {logs.map((log) => (
          <div key={log.id} className="flex items-start gap-3">
            <span className="text-[var(--color-secondary-text)] opacity-50 shrink-0 w-16">
              {log.timestamp}
            </span>
            <span className={clsx(
              'shrink-0 w-20 font-bold',
              log.type === 'INFO' && 'text-[var(--color-policy)]',
              log.type === 'CASCADE' && 'text-[var(--color-warning)]',
              log.type === 'RESULT' && 'text-[var(--color-accent)]',
              log.type === 'WARNING' && 'text-[var(--color-inflation)]'
            )}>
              [{log.type}]
            </span>
            <span className="text-[var(--color-primary-text)] break-all">
              {log.message}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
