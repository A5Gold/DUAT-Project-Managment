import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { t } from '@/lib/i18n'
import { keywordApi } from '@/lib/api'
import type { KeywordSearchResult } from '@/lib/types'

export default function KeywordSearchPage() {
  const { lastFolderPath, setLastFolderPath, setLoading, addNotification } = useAppStore()
  const [folderPath, setFolderPath] = useState(lastFolderPath)
  const [keyword, setKeyword] = useState('')
  const [results, setResults] = useState<KeywordSearchResult[]>([])
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    if (!folderPath.trim() || !keyword.trim()) return
    setLastFolderPath(folderPath)
    setLoading(true)
    setSearched(false)
    try {
      const data = (await keywordApi.search(folderPath, keyword)) as KeywordSearchResult[]
      setResults(data)
      setSearched(true)
    } catch {
      addNotification('error', t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  function highlightKeyword(text: string): React.ReactNode {
    if (!keyword.trim()) return text
    const regex = new RegExp(`(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
    const parts = text.split(regex)
    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark key={i} className="bg-yellow-200 px-0.5 rounded">{part}</mark>
      ) : (
        part
      ),
    )
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="rounded-lg bg-white p-6 shadow">
        <h1 className="mb-6 text-xl font-semibold text-gray-800">{t('keyword.title')}</h1>

        <div className="mb-4 flex flex-col gap-3 sm:flex-row">
          <input
            type="text"
            value={folderPath}
            onChange={(e) => setFolderPath(e.target.value)}
            placeholder={t('home.folderPath')}
            className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder={t('keyword.searchPlaceholder')}
            className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={handleSearch}
            disabled={!folderPath.trim() || !keyword.trim()}
            className="rounded bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {t('keyword.search')}
          </button>
        </div>

        {searched && (
          <div className="mt-4">
            <p className="mb-3 text-sm text-gray-600">
              {t('keyword.results')}: {results.length}
            </p>
            {results.length === 0 ? (
              <p className="py-8 text-center text-gray-500">{t('keyword.noResults')}</p>
            ) : (
              <div className="flex flex-col gap-3">
                {results.map((item, idx) => (
                  <div key={idx} className="rounded border border-gray-200 p-4 hover:bg-gray-50">
                    <div className="mb-1 text-sm font-medium text-gray-800">
                      {t('keyword.fileName')}: {item.file_name}
                    </div>
                    <div className="mb-1 text-xs text-gray-500">
                      {t('keyword.location')}: {item.location}
                    </div>
                    <div className="text-sm text-gray-700">
                      {t('keyword.context')}: {highlightKeyword(item.context)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
