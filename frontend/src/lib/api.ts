let port = 8000

export function setPort(p: number): void {
  port = p
}

export function getPort(): number {
  return port
}

export function getBaseUrl(): string {
  return `http://127.0.0.1:${port}`
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${getBaseUrl()}${endpoint}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const errorBody = await res.text()
    throw new Error(`API Error ${res.status}: ${errorBody}`)
  }
  return res.json() as Promise<T>
}

async function requestFormData<T>(endpoint: string, formData: FormData): Promise<T> {
  const url = `${getBaseUrl()}${endpoint}`
  const res = await fetch(url, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const errorBody = await res.text()
    throw new Error(`API Error ${res.status}: ${errorBody}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, body?: unknown) =>
    request<T>(endpoint, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(endpoint: string, body?: unknown) =>
    request<T>(endpoint, { method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
}

// --- API Groups ---

export const healthApi = {
  check: () => api.get('/api/health'),
}

export const configApi = {
  get: () => api.get('/api/config'),
  update: (data: unknown) => api.put('/api/config', data),
  reset: () => api.post('/api/config/reset'),
}

export const parseApi = {
  folder: (path: string) => api.post('/api/parse/folder', { path }),
  progress: () => api.get('/api/parse/progress'),
  results: () => api.get('/api/parse/results'),
  files: (path: string) => api.post('/api/parse/files', { path }),
}

export const dashboardApi = {
  analyze: (records: unknown) => api.post('/api/dashboard/analyze', records),
  loadExcel: (formData: FormData) => requestFormData('/api/dashboard/load-excel', formData),
  stats: () => api.get('/api/dashboard/stats'),
  summary: () => api.get('/api/dashboard/summary'),
  weeklyTrend: () => api.get('/api/dashboard/trends/weekly'),
  monthlyTrend: () => api.get('/api/dashboard/trends/monthly'),
  projectDistribution: () => api.get('/api/dashboard/distribution/projects'),
  keywordDistribution: () => api.get('/api/dashboard/distribution/keywords'),
  lineDistribution: () => api.get('/api/dashboard/distribution/lines'),
  rawData: (page: number, limit: number) =>
    api.get(`/api/dashboard/raw-data?limit=${limit}&offset=${(page - 1) * limit}`),
  pivot: () => api.get('/api/dashboard/pivot'),
  nthByProject: () => api.get('/api/dashboard/trends/nth-by-project'),
}

export const lagApi = {
  loadMaster: (formData: FormData) => requestFormData('/api/lag/load-master', formData),
  projects: () => api.get('/api/lag/projects'),
  updateConfig: (projectNo: string, config: unknown) =>
    api.put(`/api/lag/config/${projectNo}`, config),
  calculate: () => api.post('/api/lag/calculate'),
  results: () => api.get('/api/lag/results'),
  statusLegend: () => api.get('/api/lag/status-legend'),
}

export const performanceApi = {
  setData: () => api.post('/api/performance/set-data'),
  projects: () => api.get('/api/performance/projects'),
  analyze: (code: string, target: unknown) =>
    api.post(`/api/performance/analyze/${code}`, target),
  breakdown: () => api.get('/api/performance/breakdown'),
  recovery: (code: string, targetQty: number, endDate: string) =>
    api.post(`/api/performance/recovery/${code}`, { targetQty, endDate }),
  weeklyChart: (code: string) => api.get(`/api/performance/weekly-chart/${code}`),
  cumulativeChart: (code: string) => api.get(`/api/performance/cumulative-chart/${code}`),
  cumulativeData: (code: string) => api.get(`/api/performance/cumulative-data/${code}`),
}

export const scurveApi = {
  setData: () => api.post('/api/scurve/set-data'),
  calculate: (params: unknown) => api.post('/api/scurve/calculate', params),
  chart: (params: unknown) => api.post('/api/scurve/chart', params),
  excel: (params: unknown) => api.post('/api/scurve/excel', params),
}

export const exportApi = {
  dashboard: (path: string) => api.post('/api/export/dashboard', { path }),
  lagAnalysis: (path: string) => api.post('/api/export/lag-analysis', { path }),
  download: (fileType: string) => api.get(`/api/export/download/${fileType}`),
  saveDashboard: () => api.post('/api/export/save-dashboard'),
}

export const keywordApi = {
  search: (folderPath: string, keyword: string) =>
    api.post('/api/keyword/search', { folderPath, keyword }),
}

export const manpowerApi = {
  scan: (folderPath: string) => api.post('/api/manpower/scan', { folderPath }),
  analysis: () => api.get('/api/manpower/analysis'),
  exportExcel: (path: string) => api.post('/api/manpower/export-excel', { path }),
}
