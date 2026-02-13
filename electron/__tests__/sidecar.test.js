/**
 * Tests for electron/sidecar.js
 *
 * Covers: findFreePort, resolveBackendPath, checkHealth, waitUntilReady, killBackend
 */

const http = require('http');
const {
  findFreePort,
  resolveBackendPath,
  checkHealth,
  waitUntilReady,
  DEFAULTS,
} = require('../sidecar');

describe('findFreePort', () => {
  it('should return a valid port number', async () => {
    const port = await findFreePort();
    expect(port).toBeGreaterThan(0);
    expect(port).toBeLessThanOrEqual(65535);
  });

  it('should return different ports on consecutive calls', async () => {
    const port1 = await findFreePort();
    const port2 = await findFreePort();
    // Not guaranteed but extremely likely with random OS assignment
    expect(typeof port1).toBe('number');
    expect(typeof port2).toBe('number');
  });
});

describe('resolveBackendPath', () => {
  it('should return python command in dev mode', () => {
    const result = resolveBackendPath(false, '');
    expect(result.command).toBe('python');
    expect(result.args[0]).toContain('backend');
    expect(result.args[0]).toContain('main.py');
  });

  it('should return backend.exe path in packaged mode', () => {
    const result = resolveBackendPath(true, 'C:\\app\\resources');
    expect(result.command).toContain('backend.exe');
    expect(result.command).toContain('C:\\app\\resources');
    expect(result.args).toEqual([]);
  });
});

describe('checkHealth', () => {
  let server;
  let serverPort;

  afterEach(async () => {
    if (server) {
      await new Promise((resolve) => server.close(resolve));
      server = null;
    }
  });

  it('should return true when backend responds healthy', async () => {
    serverPort = await findFreePort();
    server = http.createServer((_req, res) => {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'healthy', version: '4.0.0' }));
    });
    await new Promise((resolve) => server.listen(serverPort, '127.0.0.1', resolve));

    const result = await checkHealth(serverPort);
    expect(result).toBe(true);
  });

  it('should return false when backend responds unhealthy', async () => {
    serverPort = await findFreePort();
    server = http.createServer((_req, res) => {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'starting' }));
    });
    await new Promise((resolve) => server.listen(serverPort, '127.0.0.1', resolve));

    const result = await checkHealth(serverPort);
    expect(result).toBe(false);
  });

  it('should return false when backend returns invalid JSON', async () => {
    serverPort = await findFreePort();
    server = http.createServer((_req, res) => {
      res.writeHead(200);
      res.end('not json');
    });
    await new Promise((resolve) => server.listen(serverPort, '127.0.0.1', resolve));

    const result = await checkHealth(serverPort);
    expect(result).toBe(false);
  });

  it('should return false when no server is running', async () => {
    const unusedPort = await findFreePort();
    const result = await checkHealth(unusedPort);
    expect(result).toBe(false);
  });
});

describe('waitUntilReady', () => {
  let server;
  let serverPort;

  afterEach(async () => {
    if (server) {
      await new Promise((resolve) => server.close(resolve));
      server = null;
    }
  });

  it('should resolve when backend becomes healthy', async () => {
    serverPort = await findFreePort();
    let requestCount = 0;

    server = http.createServer((_req, res) => {
      requestCount++;
      res.writeHead(200, { 'Content-Type': 'application/json' });
      // Become healthy after 2 requests
      if (requestCount >= 2) {
        res.end(JSON.stringify({ status: 'healthy' }));
      } else {
        res.end(JSON.stringify({ status: 'starting' }));
      }
    });
    await new Promise((resolve) => server.listen(serverPort, '127.0.0.1', resolve));

    await waitUntilReady(serverPort, { pollIntervalMs: 100, maxWaitMs: 5000 });
    expect(requestCount).toBeGreaterThanOrEqual(2);
  });

  it('should reject after maxWaitMs timeout', async () => {
    const unusedPort = await findFreePort();

    await expect(
      waitUntilReady(unusedPort, { pollIntervalMs: 50, maxWaitMs: 300 })
    ).rejects.toThrow('Backend not ready after 300ms');
  });

  it('should reject when aborted via signal', async () => {
    const unusedPort = await findFreePort();
    const controller = new AbortController();

    const promise = waitUntilReady(unusedPort, {
      pollIntervalMs: 100,
      maxWaitMs: 10000,
      signal: controller.signal,
    });

    setTimeout(() => controller.abort(), 150);

    await expect(promise).rejects.toThrow('Health poll aborted');
  });
});

describe('DEFAULTS', () => {
  it('should have expected default values', () => {
    expect(DEFAULTS.healthEndpoint).toBe('/api/health');
    expect(DEFAULTS.pollIntervalMs).toBe(500);
    expect(DEFAULTS.maxWaitMs).toBe(30000);
    expect(DEFAULTS.host).toBe('127.0.0.1');
  });
});
