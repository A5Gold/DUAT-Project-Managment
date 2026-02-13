/** Type definitions for the Electron preload bridge (window.electronAPI) */

interface ElectronFileFilter {
  name: string;
  extensions: string[];
}

interface ElectronAPI {
  getBackendPort: () => Promise<number | null>;
  openDirectory: () => Promise<string | null>;
  openFile: (filters?: ElectronFileFilter[]) => Promise<string | null>;
  onBackendReady: (callback: (port: number) => void) => () => void;
  onBackendError: (callback: (error: { type: string; message: string }) => void) => () => void;
  onSidecarLog: (callback: (message: string) => void) => () => void;
  appQuit: () => void;
  retrySidecar: () => Promise<{ success: boolean; error?: string }>;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export type { ElectronAPI, ElectronFileFilter };
