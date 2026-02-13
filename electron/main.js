/**
 * Electron Main Process
 *
 * Responsibilities:
 *   1. Create BrowserWindow with loading screen
 *   2. Spawn FastAPI sidecar and wait for health
 *   3. Load React SPA once backend is ready
 *   4. Handle IPC for native dialogs and sidecar lifecycle
 *   5. Graceful shutdown on window close
 */

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const {
  findFreePort,
  spawnBackend,
  waitUntilReady,
  killBackend,
} = require('./sidecar');

/** @type {BrowserWindow | null} */
let mainWindow = null;
/** @type {import('child_process').ChildProcess | null} */
let sidecarProcess = null;
/** @type {number | null} */
let backendPort = null;
/** @type {boolean} */
let isQuitting = false;

// Prevent multiple instances
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
}

/**
 * Get the path to the loading HTML file.
 */
function getLoadingPagePath() {
  return path.join(__dirname, 'loading.html');
}

/**
 * Get the path to the built React SPA index.html.
 * In dev mode, try Vite dev server first; fall back to built files.
 */
async function getAppUrl() {
  if (process.env.DUAT_ENV === 'development') {
    try {
      const res = await fetch('http://127.0.0.1:3000', { signal: AbortSignal.timeout(1000) });
      if (res.ok) return 'http://127.0.0.1:3000';
    } catch {
      // Vite dev server not running, fall back to built files
    }
  }
  return `file://${path.join(__dirname, '..', 'frontend', 'dist', 'index.html')}`;
}

/**
 * Create the main application window.
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    show: false,
    title: 'MTR DUAT v4.0.0',
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  // Show window when ready to avoid white flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  return mainWindow;
}

/**
 * Start the sidecar backend and wait for it to become healthy.
 * Sends status events to the renderer via IPC.
 */
async function startSidecar() {
  backendPort = await findFreePort();

  const isPackaged = app.isPackaged;
  const resourcesPath = isPackaged ? process.resourcesPath : '';

  sidecarProcess = spawnBackend(backendPort, {
    isPackaged,
    resourcesPath,
    onStdout: (msg) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('sidecar:log', msg);
      }
    },
    onStderr: (msg) => {
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('sidecar:log', msg);
      }
    },
    onExit: (code, signal) => {
      if (!isQuitting && mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('backend:error', {
          type: 'crash',
          message: `Backend exited unexpectedly (code=${code}, signal=${signal})`,
        });
      }
      sidecarProcess = null;
    },
  });

  const abortController = new AbortController();

  // If the child dies before becoming healthy, abort the wait
  sidecarProcess.on('exit', () => abortController.abort());

  await waitUntilReady(backendPort, {
    pollIntervalMs: 500,
    maxWaitMs: 30000,
    signal: abortController.signal,
  });
}

/**
 * Load the React SPA into the main window.
 */
async function loadApp() {
  if (!mainWindow || mainWindow.isDestroyed()) return;

  const appUrl = await getAppUrl();
  await mainWindow.loadURL(appUrl);
  mainWindow.webContents.send('backend:ready', backendPort);
}

// ─── IPC Handlers ────────────────────────────────────────────

/** Return the current backend port */
ipcMain.handle('sidecar:getPort', () => backendPort);

/** Native directory picker */
ipcMain.handle('dialog:openDirectory', async () => {
  if (!mainWindow) return null;
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
  });
  if (result.canceled || result.filePaths.length === 0) return null;
  return result.filePaths[0];
});

/** Native file picker with optional filters */
ipcMain.handle('dialog:openFile', async (_event, filters) => {
  if (!mainWindow) return null;
  const options = {
    properties: ['openFile'],
  };
  if (filters && Array.isArray(filters)) {
    options.filters = filters;
  }
  const result = await dialog.showOpenDialog(mainWindow, options);
  if (result.canceled || result.filePaths.length === 0) return null;
  return result.filePaths[0];
});

/** Retry sidecar startup */
ipcMain.handle('sidecar:retry', async () => {
  try {
    if (sidecarProcess) {
      await killBackend(sidecarProcess);
      sidecarProcess = null;
    }
    await startSidecar();
    await loadApp();
    return { success: true };
  } catch (err) {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend:error', {
        type: 'startup_failed',
        message: err.message,
      });
    }
    return { success: false, error: err.message };
  }
});

/** Quit the app */
ipcMain.on('app:quit', () => {
  app.quit();
});

// ─── App Lifecycle ───────────────────────────────────────────

app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  }
});

app.whenReady().then(async () => {
  const win = createWindow();

  // Show loading screen first
  await win.loadFile(getLoadingPagePath());
  win.show();

  try {
    await startSidecar();
    await loadApp();
  } catch (err) {
    if (win && !win.isDestroyed()) {
      win.webContents.send('backend:error', {
        type: 'startup_failed',
        message: err.message,
      });
    }
  }
});

app.on('before-quit', async (event) => {
  if (isQuitting) return;
  isQuitting = true;
  event.preventDefault();

  if (sidecarProcess) {
    await killBackend(sidecarProcess);
    sidecarProcess = null;
  }
  app.quit();
});

app.on('window-all-closed', () => {
  app.quit();
});
