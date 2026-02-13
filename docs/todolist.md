# 專案進度追蹤

## MTR PS-OHLR DUAT - 重建計劃任務清單

**版本**: 4.0.0
**最後更新**: 2026-02-14 (Phase 4A 打包完成，Bug 修復 3 項，Dashboard API 整合測試 35 項通過)

---

## 總覽

| 階段 | 名稱 | 狀態 | 任務數 | 完成數 | 進度 |
|------|------|------|--------|--------|------|
| Phase 0 | 基礎建設 | DONE | 5 | 5 | 100% |
| Phase 1 | 後端完善 | DONE | 19 | 19 | 100% |
| Phase 2 | 前端開發 | DONE | 25 | 25 | 100% |
| Phase 3 | Electron 整合 | DONE | 6 | 6 | 100% |
| Phase 4 | 打包與測試 | IN PROGRESS | 10 | 6 | 60% |

### Bug 修復追蹤

| # | Bug | 狀態 | 修復檔案 | 根因 |
|---|-----|------|----------|------|
| BF-1 | 語言切換按鍵 zh/en 無效 | DONE | `Sidebar.tsx`, `Layout.tsx` | Sidebar 只更新 Zustand store 未呼叫 `setLocale()`；Layout 未訂閱 language 導致子頁面不重新渲染 |
| BF-2 | `npm run dev` 白屏 (ERR_CONNECTION_REFUSED) | DONE | `electron/main.js` | 開發模式硬編碼載入 Vite dev server URL，未啟動時無 fallback；改為 async 偵測後 fallback 至 `file://` |
| BF-3 | Dashboard 進入時 API 404 | DONE | `frontend/src/lib/api.ts` | 前端 API 路徑與後端路由不匹配（如 `/weekly-trend` vs `/trends/weekly`）；已對齊全部 10 個 GET 端點 |

---

## Phase 0：基礎建設 — DONE

| # | 任務 | 狀態 | 產出 |
|---|------|------|------|
| 0.1 | 初始化 monorepo 結構 | DONE | `pyproject.toml` |
| 0.2 | 配置 pytest + coverage | DONE | `pyproject.toml`, `tests/conftest.py` |
| 0.3 | 建立 parsers/ 套件骨架 | DONE | `parsers/__init__.py` |
| 0.4 | 建立 utils/ 套件骨架 | DONE | `utils/__init__.py` |
| 0.5 | 修正 `__init__.py` 匯出名稱 (TD-3) | DONE | `analysis/__init__.py` |

---

## Phase 1：後端完善 — DONE

### 1A. 外部依賴模組開發

| # | 任務 | 狀態 | 測試數 | 覆蓋率 |
|---|------|------|--------|--------|
| 1.1 | `config.py` 設定模組 | DONE | 25 | 98% |
| 1.2 | `parsers/docx_parser.py` DOCX 解析器 | DONE | 49 | 87% |
| 1.3 | `parsers/manpower_parser.py` 人力解析器 | DONE | 70 | 98% |
| 1.4 | `utils/excel_export.py` Excel 匯出工具 | DONE | 14 | 96% |

### 1B. 後端修改

| # | 任務 | 狀態 | 說明 |
|---|------|------|------|
| 1.5 | `backend/main.py` 加入 `--port` CLI 參數 | DONE | argparse + --host/--port |
| 1.6 | `backend/main.py` 版本升級至 4.0.0 | DONE | version="4.0.0" |
| 1.7 | `backend/main.py` CORS 改為環境變數配置 | DONE | DUAT_CORS_ORIGINS |
| 1.8 | `backend/main.py` 標準化日誌格式 | DONE | logging.basicConfig |
| 1.9 | `routers/config.py` 移除 tkinter browse | DONE | 改為 501 + Electron IPC 提示 |

### 1C. 單元測試

| # | 任務 | 狀態 | 測試數 | 覆蓋率 |
|---|------|------|--------|--------|
| 1.10 | `analysis/dashboard.py` 測試 | DONE | 25 | 86% |
| 1.11 | `analysis/lag_analysis.py` 測試 | DONE | 19 | 88% |
| 1.12 | `analysis/performance.py` 測試 | DONE | 18 | 97% |
| 1.13 | `analysis/scurve.py` 測試 | DONE | 16 | 96% |
| 1.14 | `analysis/manpower.py` 測試 | DONE | 27 | 98% |

### 1D. 品質驗證

| # | 任務 | 狀態 | 結果 |
|---|------|------|------|
| 1.15 | 完整測試套件通過 | DONE | 330 passed |
| 1.16 | 覆蓋率達 80%+ | DONE | 92.57% |

---

## Phase 2：前端開發 — DONE

### 2A. React SPA 腳手架

| # | 任務 | 狀態 | 產出 |
|---|------|------|------|
| 2.1 | 配置 Vite + React + TypeScript | DONE | `frontend/` 目錄 |
| 2.2 | 配置 Tailwind CSS + Preline UI | DONE | `tailwind.config.js` |
| 2.3 | 配置 ESLint + Prettier | DONE | `.prettierrc`, vitest |
| 2.4 | 建立 `lib/types.ts` 型別定義 | DONE | 26 個 TypeScript 型別 |
| 2.5 | 建立 `lib/api.ts` API 客戶端 | DONE | 動態 port HTTP 客戶端 + 10 個 API 群組 |
| 2.6 | 建立 `lib/store.ts` Zustand 狀態管理 | DONE | AppState store |

### 2B. 共用元件

| # | 任務 | 狀態 | 產出 |
|---|------|------|------|
| 2.7 | `Layout.tsx` 側邊欄 + 頂部導航 | DONE | 主佈局框架 |
| 2.8 | `Sidebar.tsx` 導航選單 | DONE | 7 頁面導航 + 語言切換 |
| 2.9 | `LoadingOverlay.tsx` 載入中覆蓋層 | DONE | 全域載入指示 |
| 2.10 | `NotificationToast.tsx` 通知提示 | DONE | 成功/錯誤通知 + 自動消失 |
| 2.11 | `tables/DataTable.tsx` 通用數據表格 | DONE | 分頁 + 排序 |
| 2.12 | `tables/PivotTable.tsx` 樞紐分析表 | DONE | NTH 樞紐表 |

### 2C. Chart.js 圖表元件

| # | 任務 | 狀態 | 產出 |
|---|------|------|------|
| 2.13 | `charts/BarChart.tsx` | DONE | 長條圖封裝 |
| 2.14 | `charts/LineChart.tsx` | DONE | 折線圖封裝 |
| 2.15 | `charts/PieChart.tsx` | DONE | 圓餅圖封裝 |
| 2.16 | `charts/SCurveChart.tsx` | DONE | S-Curve 專用圖表 |

### 2D. 頁面開發（按依賴順序）

| # | 頁面 | 狀態 | API 端點 | 主要元件 |
|---|------|------|----------|----------|
| 2.17 | `HomePage.tsx` 首頁 | DONE | `/api/config`, `/api/parse/*` | FolderPicker, ParseProgress |
| 2.18 | `GeneratePage.tsx` 生成儀表板 | DONE | `/api/dashboard/analyze`, `load-excel` | AnalyzeButton, ExcelUpload |
| 2.19 | `DashboardPage.tsx` 儀表板 | DONE | `/api/dashboard/*` (12 端點) | StatsCards, 6 Charts, DataTable |
| 2.20 | `LagAnalysisPage.tsx` 滯後分析 | DONE | `/api/lag/*` (6 端點) | FileUpload, ConfigEditor, ResultTable |
| 2.21 | `PerformancePage.tsx` 績效追蹤 | DONE | `/api/performance/*` (8 端點) | ProjectSelector, PerfChart |
| 2.22 | `KeywordSearchPage.tsx` 關鍵字搜尋 | DONE | `/api/keyword/search` | SearchInput, ResultList |
| 2.23 | `ManpowerPage.tsx` 人力分析 | DONE | `/api/manpower/*` (3 端點) | KPICards, RoleTable, TeamChart |

### 2E. 國際化

| # | 任務 | 狀態 | 產出 |
|---|------|------|------|
| 2.24 | `lib/i18n.ts` 國際化模組 | DONE | en/zh 翻譯函式 |
| 2.25 | 所有頁面套用 i18n | DONE | 中英文切換 |

---

## Phase 3：Electron 整合 — DONE

| # | 任務 | 狀態 | 產出 |
|---|------|------|------|
| 3.1 | `electron/main.js` BrowserWindow 建立 | DONE | 視窗管理 + 多實例防護 |
| 3.2 | `electron/sidecar.js` Sidecar 管理器 | DONE | spawn/kill/health-poll (12 tests) |
| 3.3 | `electron/preload.js` IPC 橋接 | DONE | `window.electronAPI` + TypeScript 型別 |
| 3.4 | 原生檔案對話框 IPC | DONE | `dialog:openDirectory`, `dialog:openFile` |
| 3.5 | 載入畫面（等待 Sidecar 就緒） | DONE | Loading screen + 進度日誌 |
| 3.6 | 錯誤處理（Sidecar 啟動失敗） | DONE | 重試/退出對話框 + crash 偵測 |

---

## Phase 4：打包與測試 — IN PROGRESS

### 4A. 打包配置

| # | 任務 | 狀態 | 產出 |
|---|------|------|------|
| 4.1 | PyInstaller 後端打包 | DONE | `backend.spec`, `scripts/build.py` |
| 4.2 | `npm run build` 前端建置 | DONE | `frontend/dist/`（腳本已配置） |
| 4.3 | electron-builder 配置 | DONE | `electron-builder.yml` |
| 4.4 | 可攜式 .exe 打包 | DONE | `build/MTR_DUAT_4.0.0.exe`（113 MB） |

### 4B. 驗證

| # | 驗證項目 | 狀態 | 測試方法 |
|---|----------|------|----------|
| 4.5 | 無 Python 環境啟動 | TODO | 乾淨 Windows VM |
| 4.6 | 無 Node.js 環境啟動 | TODO | 乾淨 Windows VM |
| 4.7 | SharePoint 同步資料夾讀取 | TODO | 指向 SharePoint 路徑 |
| 4.8 | 設定檔持久化 | TODO | 關閉重開驗證 |

### 4C. 測試計劃文件

| # | 文件 | 狀態 | 產出 |
|---|------|------|------|
| 4.9 | E2E 測試計劃 | DONE | `docs/e2e-test-plan.md`（16 場景） |
| 4.10 | UAT 驗收測試計劃 | DONE | `docs/uat-test-plan.md`（74 測試項目） |

---

## 里程碑追蹤

| 里程碑 | 交付物 | 狀態 | 驗收標準 |
|--------|--------|------|----------|
| M0 | 專案腳手架 | DONE | pytest 可執行 |
| M1 | 後端完善 | DONE | 330 tests passed, 92.57% coverage |
| M2 | 前端 MVP | DONE | Home + Dashboard 頁面可操作, build 成功 |
| M3 | 前端完整 | DONE | 全部 7 頁面 + i18n, 25 前端測試通過 |
| M4 | Electron 整合 | DONE | Sidecar 自動管理, 12 electron tests + 25 frontend tests |
| M5 | 可攜式 .exe | IN PROGRESS | 打包配置完成，待執行 build + VM 驗證 |
| M6 | UAT 完成 | TODO | 使用者驗收（74 測試項目已規劃） |

---

## 技術債務追蹤

| ID | 債務 | 嚴重程度 | 狀態 | 處理階段 |
|----|------|----------|------|----------|
| TD-1 | 全域可變單例 x7 | 嚴重 | DONE | Phase 2 (services.py 集中管理) |
| TD-2 | config browse 安全風險 | 嚴重 | DONE | Phase 1 |
| TD-3 | `__init__.py` 匯出名稱錯誤 | 嚴重 | DONE | Phase 0 |
| TD-4 | 外部模組缺失 x4 | 嚴重 | DONE | Phase 1 |
| TD-5 | 無測試覆蓋 | 高 | DONE | Phase 1 (92.57%) |
| TD-6 | 硬編碼關鍵字 | 高 | DONE | Phase 1 (config.py keywords) |
| TD-7 | Week->Month 近似公式 | 高 | DONE | Phase 1 (DateObj.dt.strftime) |
| TD-8 | 跨路由耦合 | 高 | DONE | Phase 2 (services.py 共享服務層) |
| TD-9 | 無日誌標準化 | 中 | DONE | Phase 2 (全部 9 模組 + services) |
| TD-10 | CORS 硬編碼 | 中 | DONE | Phase 1 |
| TD-11 | 第 53 週問題 | 中 | DONE | Phase 1 (isocalendar) |

### 新增測試

| # | 測試檔案 | 狀態 | 測試數 | 說明 |
|---|----------|------|--------|------|
| T-1 | `tests/test_dashboard_api.py` | DONE | 35 | Dashboard API 端點整合測試（含 mock data、正常/無資料兩種情境） |
