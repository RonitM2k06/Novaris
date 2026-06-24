import { create } from 'zustand';

export type TabType = 'ScenarioStudio' | 'HistoricalReplay' | 'OntologyExplorer' | 'CalibrationLab' | 'ResearchReports';

export interface Tab {
  id: string;
  type: TabType;
  title: string;
}

export interface LogEntry {
  id: string;
  type: 'INFO' | 'CASCADE' | 'RESULT' | 'WARNING';
  message: string;
  timestamp: string;
}

interface WorkspaceState {
  tabs: Tab[];
  activeTabId: string | null;
  logs: LogEntry[];
  contextData: any;
  
  openTab: (tab: Tab) => void;
  closeTab: (tabId: string) => void;
  setActiveTab: (tabId: string) => void;
  addLog: (log: Omit<LogEntry, 'id' | 'timestamp'>) => void;
  setContextData: (data: any) => void;
  clearLogs: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  tabs: [{ id: 'scenario-studio', type: 'ScenarioStudio', title: 'Scenario Studio' }],
  activeTabId: 'scenario-studio',
  logs: [
    { id: '1', type: 'INFO', message: 'Novaris Command Center Initialized.', timestamp: 'SYSTEM' }
  ],
  contextData: null,
  
  openTab: (tab) => set((state) => {
    const exists = state.tabs.find((t) => t.id === tab.id);
    if (exists) {
      return { activeTabId: tab.id };
    }
    return { tabs: [...state.tabs, tab], activeTabId: tab.id };
  }),
  
  closeTab: (tabId) => set((state) => {
    const newTabs = state.tabs.filter((t) => t.id !== tabId);
    let newActive = state.activeTabId;
    if (state.activeTabId === tabId) {
      newActive = newTabs.length > 0 ? newTabs[newTabs.length - 1].id : null;
    }
    return { tabs: newTabs, activeTabId: newActive };
  }),
  
  setActiveTab: (tabId) => set({ activeTabId: tabId }),
  
  addLog: (log) => set((state) => ({
    logs: [...state.logs, { ...log, id: Math.random().toString(), timestamp: new Date().toLocaleTimeString() }]
  })),
  
  setContextData: (data) => set({ contextData: data }),
  
  clearLogs: () => set({ logs: [] })
}));
