'use client';

import React, { useEffect, useState } from 'react';
import { useWorkspaceStore } from '../../store/workspace';
import { FileText } from 'lucide-react';
import { clsx } from 'clsx';

export default function ResearchReports() {
  const { setContextData } = useWorkspaceStore();
  const [reports, setReports] = useState<any[]>([]);
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null);

  useEffect(() => {
    const fetchReports = async () => {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      try {
        const res = await fetch(`${API_URL}/reports`);
        const data = await res.json();
        if (data.reports) {
          setReports(data.reports);
          if (data.reports.length > 0) {
            setSelectedFilename(data.reports[0].filename);
          }
        }
      } catch (e) {
        // Silent fail
      }
    };
    fetchReports();
  }, []);

  useEffect(() => {
    setContextData({
      'Document Metadata': {
        'Filename': selectedFilename || 'None',
        'Author': 'Novaris Autonomous System',
        'Status': 'Validated'
      }
    });
  }, [selectedFilename, setContextData]);

  const selectedReport = reports.find(r => r.filename === selectedFilename);

  return (
    <div className="flex h-full text-[var(--color-primary-text)]">
      {/* Sidebar List */}
      <div className="w-64 border-r border-[var(--color-edge)] bg-black/20 overflow-y-auto">
        <div className="p-4 border-b border-[var(--color-edge)]">
          <h2 className="text-xs font-bold tracking-widest uppercase">RESEARCH REPORTS</h2>
        </div>
        <div className="flex flex-col">
          {reports.map(r => (
            <button
              key={r.filename}
              onClick={() => setSelectedFilename(r.filename)}
              className={clsx(
                'text-left p-4 border-b border-[var(--color-edge)] transition-colors',
                selectedFilename === r.filename ? 'bg-[var(--color-edge)]' : 'hover:bg-[var(--color-panel)]'
              )}
            >
              <div className="flex items-center gap-2 mb-1">
                <FileText size={14} className="text-[var(--color-secondary-text)]" />
              </div>
              <h3 className="text-sm font-semibold truncate" title={r.filename}>{r.filename.replace('.md', '').replace(/_/g, ' ')}</h3>
            </button>
          ))}
          {reports.length === 0 && (
            <div className="p-4 text-xs text-[var(--color-secondary-text)] italic">No reports found.</div>
          )}
        </div>
      </div>

      {/* Report Content */}
      <div className="flex-1 p-8 overflow-y-auto font-sans leading-relaxed">
        {selectedReport ? (
          <div className="max-w-3xl whitespace-pre-wrap">
            {selectedReport.content}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-[var(--color-secondary-text)] opacity-50">
            Select a report to view content.
          </div>
        )}
      </div>
    </div>
  );
}
