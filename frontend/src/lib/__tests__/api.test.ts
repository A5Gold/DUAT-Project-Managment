import { describe, it, expect, vi, beforeEach } from 'vitest'
import { getBaseUrl, setPort, api } from '@/lib/api'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

beforeEach(() => {
  mockFetch.mockReset()
  setPort(8000)
})

describe('getBaseUrl', () => {
  it('returns correct URL with default port 8000', () => {
    expect(getBaseUrl()).toBe('http://127.0.0.1:8000')
  })

  it('uses custom port when set via setPort()', () => {
    setPort(9999)
    expect(getBaseUrl()).toBe('http://127.0.0.1:9999')
  })
})

describe('api.get', () => {
  it('calls fetch with correct URL and returns data', async () => {
    const mockData = { message: 'hello' }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    })

    const result = await api.get('/api/health')

    expect(mockFetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/health', {
      headers: { 'Content-Type': 'application/json' },
    })
    expect(result).toEqual(mockData)
  })

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      text: () => Promise.resolve('Not Found'),
    })

    await expect(api.get('/api/missing')).rejects.toThrow('API Error 404: Not Found')
  })
})

describe('api.post', () => {
  it('calls fetch with correct URL, method POST, and JSON body', async () => {
    const mockData = { id: 1 }
    const body = { name: 'test' }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    })

    const result = await api.post('/api/items', body)

    expect(mockFetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/items', {
      headers: { 'Content-Type': 'application/json' },
      method: 'POST',
      body: JSON.stringify(body),
    })
    expect(result).toEqual(mockData)
  })

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: () => Promise.resolve('Internal Server Error'),
    })

    await expect(api.post('/api/fail', { data: 1 })).rejects.toThrow(
      'API Error 500: Internal Server Error',
    )
  })
})
