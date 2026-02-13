import { useState, useEffect, useRef, useCallback } from 'react'
import { useAppStore } from '@/lib/store'
import { t } from '@/lib/i18n'
import { parseApi, configApi } from '@/lib/api'
import type { ParseProgress, AppConfig } from '@/lib/types'

export default function HomePage() {
  const { lastFolderPath, setLastFolderPath, setLoading, addNotification } = useAppStore()
  const [folderPath, setFolderPath] = useState(lastFolderPath)
  const [progress, setProgress] = useState<ParseProgress | null>(null)
  const [isParsing, setIsParsing] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    configApi.get().then((config) => {
      const appConfig = config as AppConfig
      if (appConfig.last_folder) {
        setFolderPath(appConfig.last_folder)
        setLastFolderPath(appConfig.last_folder)
      }
    }).catch(() => {
      // config not available yet
    })
  }, [setLastFolderPath])

  const stopPolling = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [])

  const pollProgress = useCallback(() => {
    timerRef.current = setInterval(async () => {
      try {
        const data = (await parseApi.progress()) as ParseProgress
        setProgress(data)
        if (data.status === 'complete') {
          stopPolling()
          setIsParsing(false)
          setLoading(false)
          addNotification('success', t('home.parseComplete'))
        } else if (data.status === 'error') {
          stopPolling()
          setIsParsing(false)
          setLoading(false)
          addNotification('error', data.error ?? t('common.error'))
        }
      } catch {
        stopPolling()
        setIsParsing(false)
        setLoading(false)
      }
    }, 1000)
  }, [stopPolling, setLoading, addNotification])

  useEffect(() => {
    return () => stopPolling()
  }, [stopPolling])

  const handleBrowse = async () => {
    if (window.electronAPI) {
      const selected = await window.electronAPI.openDirectory()
      if (selected) {
        setFolderPath(selected)
        setLastFolderPath(selected)
      }
    }
  }

  const handleStartParse = async () => {
    if (!folderPath.trim()) {
      addNotification('warning', t('home.noFolder'))
      return
    }
    setLastFolderPath(folderPath)
    setIsParsing(true)
    setLoading(true)
    setProgress(null)
    try {
      await parseApi.folder(folderPath)
      pollProgress()
    } catch {
      setIsParsing(false)
      setLoading(false)
      addNotification('error', t('common.error'))
    }
  }

  const percentage = progress ? Math.round(progress.progress * 100) : 0

  return (
    <div className="mx-auto max-w-2xl p-6">
      <div className="rounded-lg bg-white p-6 shadow">
        <h1 className="mb-6 text-xl font-semibold text-gray-800">{t('home.title')}</h1>

        <label className="mb-1 block text-sm font-medium text-gray-600">
          {t('home.folderPath')}
        </label>
        <div className="mb-4 flex gap-2">
          <input
            type="text"
            value={folderPath}
            onChange={(e) => setFolderPath(e.target.value)}
            placeholder={t('home.noFolder')}
            className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={handleBrowse}
            className="rounded bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            {t('home.selectFolder')}
          </button>
        </div>

        <button
          type="button"
          onClick={handleStartParse}
          disabled={!folderPath.trim() || isParsing}
          className="w-full rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isParsing ? t('home.parsing') : t('home.startParse')}
        </button>

        {progress && (
          <div className="mt-6">
            <div className="mb-1 flex items-center justify-between text-sm text-gray-600">
              <span>{progress.current_file}</span>
              <span>{percentage}%</span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">
              <div
                className="h-full rounded-full bg-blue-600 transition-all duration-300"
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
