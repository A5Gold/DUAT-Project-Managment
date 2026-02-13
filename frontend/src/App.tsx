import { useEffect, useState } from 'react'
import { HashRouter, BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from '@/components/Layout'
import HomePage from '@/pages/HomePage'
import GeneratePage from '@/pages/GeneratePage'
import DashboardPage from '@/pages/DashboardPage'
import LagAnalysisPage from '@/pages/LagAnalysisPage'
import PerformancePage from '@/pages/PerformancePage'
import KeywordSearchPage from '@/pages/KeywordSearchPage'
import ManpowerPage from '@/pages/ManpowerPage'
import { setPort } from '@/lib/api'

const isElectron = !!window.electronAPI
const Router = isElectron ? HashRouter : BrowserRouter

function App() {
  const [ready, setReady] = useState(!isElectron)

  useEffect(() => {
    if (!window.electronAPI) return

    window.electronAPI.getBackendPort().then((port) => {
      if (port) {
        setPort(port)
        setReady(true)
      }
    })

    const cleanup = window.electronAPI.onBackendReady((port) => {
      setPort(port)
      setReady(true)
    })

    return cleanup
  }, [])

  if (!ready) return null

  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/generate" element={<GeneratePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/lag-analysis" element={<LagAnalysisPage />} />
          <Route path="/performance" element={<PerformancePage />} />
          <Route path="/keyword-search" element={<KeywordSearchPage />} />
          <Route path="/manpower" element={<ManpowerPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
