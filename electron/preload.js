/**
 * Preload script — exposes a safe subset of Electron APIs to the renderer
 * via contextBridge as `window.electronAPI`.
 *
 * Exposed channels:
 *   - getBackendPort()       → returns the sidecar port number
 *   - openDirectory()        → native folder picker dialog
 *   - openFile(filters?)     → native file picker dialog
 *   - onBackendReady(cb)     → listen for sidecar ready event
 *   - onBackendError(cb)     → listen for sidecar error event
 *   - onSidecarLog(cb)       → listen for sidecar stdout/stderr
 *   - appQuit()              → request app quit
 *   - retrySidecar()         → request sidecar restart
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  /** Get the dynamically assigned backend port */
  getBackendPort: () => ipcRenderer.invoke('sidecar:getPort'),

  /** Open a native directory picker dialog */
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),

  /** Open a native file picker dialog with optional filters */
  openFile: (filters) => ipcRenderer.invoke('dialog:openFile', filters),

  /** Listen for backend ready event (port is passed as argument) */
  onBackendReady: (callback) => {
    const handler = (_event, port) => callback(port);
    ipcRenderer.on('backend:ready', handler);
    return () => ipcRenderer.removeListener('backend:ready', handler);
  },

  /** Listen for backend error event */
  onBackendError: (callback) => {
    const handler = (_event, error) => callback(error);
    ipcRenderer.on('backend:error', handler);
    return () => ipcRenderer.removeListener('backend:error', handler);
  },

  /** Listen for sidecar log output */
  onSidecarLog: (callback) => {
    const handler = (_event, message) => callback(message);
    ipcRenderer.on('sidecar:log', handler);
    return () => ipcRenderer.removeListener('sidecar:log', handler);
  },

  /** Request the app to quit */
  appQuit: () => ipcRenderer.send('app:quit'),

  /** Request sidecar restart */
  retrySidecar: () => ipcRenderer.invoke('sidecar:retry'),
});
