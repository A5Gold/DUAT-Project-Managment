import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import LoadingOverlay from './LoadingOverlay'
import NotificationToast from './NotificationToast'
import { t } from '@/lib/i18n'
import { useAppStore } from '@/lib/store'

const pageTitleKeys: Record<string, string> = {
  '/': 'home.title',
  '/generate': 'generate.title',
  '/dashboard': 'dashboard.title',
  '/lag-analysis': 'lag.title',
  '/performance': 'performance.title',
  '/keyword-search': 'keyword.title',
  '/manpower': 'manpower.title',
}

function Layout() {
  const location = useLocation()
  const language = useAppStore((s) => s.language)
  const titleKey = pageTitleKeys[location.pathname] ?? 'app.title'

  return (
    <div className="flex min-h-screen" key={language}>
      <Sidebar />
      <div className="ml-64 min-h-screen bg-gray-50 flex-1 flex flex-col">
        <header className="p-4 bg-white shadow-sm">
          <h2 className="text-lg font-semibold text-gray-800">{t(titleKey)}</h2>
        </header>
        <main className="p-6 flex-1">
          <Outlet />
        </main>
      </div>
      <LoadingOverlay />
      <NotificationToast />
    </div>
  )
}

export default Layout
