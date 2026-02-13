/**
 * Sidecar Manager — spawns, monitors, and kills the FastAPI backend process.
 *
 * Lifecycle:
 *   1. findFreePort()  → pick an available TCP port
 *   2. spawn()         → launch `python backend/main.py --port N`
 *   3. waitUntilReady()→ poll GET /api/health every 500ms
 *   4. kill()          → SIGTERM the child process on app quit
 */

const { spawn: cpSpawn } = require('child_process');
const path = require('path');
const net = require('net');
const http = require('http');

/** Default configuration */
const DEFAULTS = {
  healthEndpoint: '/api/health',
  pollIntervalMs: 500,
  maxWaitMs: 30000,
  host: '127.0.0.1',
};

/**
 * Find a free TCP port by binding to port 0 and reading the assigned port.
 * @returns {Promise<number>}
 */
function findFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, DEFAULTS.host, () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
  });
}

/**
 * Resolve the path to the Python backend executable.
 * In production (packaged), uses the extraResources path.
 * In development, uses the source tree directly.
 * @param {boolean} isPackaged - whether the app is packaged
 * @param {string} resourcesPath - app.getPath('exe') parent or process.resourcesPath
 * @returns {{ command: string, args: string[] }}
 */
function resolveBackendPath(isPackaged, resourcesPath) {
  if (isPackaged) {
    const backendExe = path.join(resourcesPath, 'backend', 'backend.exe');
    return { command: backendExe, args: [] };
  }
  const backendScript = path.join(__dirname, '..', 'backend', 'main.py');
  return { command: 'python', args: [backendScript] };
}

/**
 * Perform a single HTTP GET health check.
 * @param {number} port
 * @returns {Promise<boolean>}
 */
function checkHealth(port) {
  return new Promise((resolve) => {
    const req = http.get(
      {
        hostname: DEFAULTS.host,
        port,
        path: DEFAULTS.healthEndpoint,
        timeout: 2000,
      },
      (res) => {
        let body = '';
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          try {
            const data = JSON.parse(body);
            resolve(data.status === 'healthy');
          } catch {
            resolve(false);
          }
        });
      }
    );
    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
  });
}

/**
 * Poll the health endpoint until the backend reports healthy.
 * @param {number} port
 * @param {{ pollIntervalMs?: number, maxWaitMs?: number, signal?: AbortSignal }} opts
 * @returns {Promise<void>}
 */
function waitUntilReady(port, opts = {}) {
  const pollInterval = opts.pollIntervalMs ?? DEFAULTS.pollIntervalMs;
  const maxWait = opts.maxWaitMs ?? DEFAULTS.maxWaitMs;

  return new Promise((resolve, reject) => {
    const start = Date.now();
    let timer = null;

    const cleanup = () => {
      if (timer) clearTimeout(timer);
    };

    if (opts.signal) {
      opts.signal.addEventListener('abort', () => {
        cleanup();
        reject(new Error('Health poll aborted'));
      }, { once: true });
    }

    const poll = async () => {
      if (opts.signal?.aborted) return;

      const elapsed = Date.now() - start;
      if (elapsed >= maxWait) {
        cleanup();
        reject(new Error(`Backend not ready after ${maxWait}ms`));
        return;
      }

      const healthy = await checkHealth(port);
      if (healthy) {
        cleanup();
        resolve();
      } else {
        timer = setTimeout(poll, pollInterval);
      }
    };

    poll();
  });
}

/**
 * Spawn the backend sidecar process.
 * @param {number} port
 * @param {{ isPackaged?: boolean, resourcesPath?: string, onStdout?: function, onStderr?: function, onExit?: function }} opts
 * @returns {import('child_process').ChildProcess}
 */
function spawnBackend(port, opts = {}) {
  const isPackaged = opts.isPackaged ?? false;
  const resourcesPath = opts.resourcesPath ?? '';
  const { command, args } = resolveBackendPath(isPackaged, resourcesPath);

  const child = cpSpawn(command, [...args, '--port', String(port)], {
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
  });

  if (opts.onStdout && child.stdout) {
    child.stdout.on('data', (data) => opts.onStdout(data.toString()));
  }
  if (opts.onStderr && child.stderr) {
    child.stderr.on('data', (data) => opts.onStderr(data.toString()));
  }
  if (opts.onExit) {
    child.on('exit', (code, signal) => opts.onExit(code, signal));
  }

  return child;
}

/**
 * Kill the sidecar process gracefully.
 * On Windows, uses taskkill /T to kill the process tree.
 * @param {import('child_process').ChildProcess} child
 * @returns {Promise<void>}
 */
function killBackend(child) {
  if (!child || child.killed) return Promise.resolve();

  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      try { child.kill('SIGKILL'); } catch { /* already dead */ }
      resolve();
    }, 5000);

    child.on('exit', () => {
      clearTimeout(timeout);
      resolve();
    });

    if (process.platform === 'win32') {
      try {
        cpSpawn('taskkill', ['/pid', String(child.pid), '/T', '/F'], {
          stdio: 'ignore',
          windowsHide: true,
        });
      } catch {
        child.kill();
      }
    } else {
      child.kill('SIGTERM');
    }
  });
}

module.exports = {
  findFreePort,
  resolveBackendPath,
  checkHealth,
  waitUntilReady,
  spawnBackend,
  killBackend,
  DEFAULTS,
};
