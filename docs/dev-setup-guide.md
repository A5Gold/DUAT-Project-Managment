# 開發環境設置指南

## MTR PS-OHLR DUAT v4.0.0 — 在新電腦上繼續開發

**最後更新**: 2026-02-14

---

## 1. 前置需求

| 軟體 | 版本 | 下載連結 | 用途 |
|------|------|----------|------|
| Python | 3.12+ | python.org/downloads | 後端 FastAPI + 分析模組 |
| Node.js | 20.x LTS | nodejs.org | Electron + React 前端 |
| Git | 最新版 | git-scm.com | 版本控制 |
| VS Code 或 Zed | 最新版 | 選用 | IDE |

安裝 Python 時勾選 "Add Python to PATH"。

---

## 2. 快速開始（5 分鐘）

在 PowerShell 或 CMD 中依序執行：

```bash
# 1. Clone 專案
git clone https://github.com/A5Gold/DUAT-Project-Managment.git
cd DUAT-Project-Managment

# 2. Python 虛擬環境
python -m venv .venv
.venv\Scripts\activate

# 3. 安裝 Python 依賴（生產 + 開發）
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 安裝根目錄 Node 依賴（Electron + electron-builder）
npm install

# 5. 安裝前端依賴
cd frontend
npm install
cd ..
```

---

## 3. 驗證環境

```bash
# 後端測試（應全部通過，365+ tests）
pytest tests/ --cov --cov-report=term-missing

# 前端 TypeScript 檢查
cd frontend && npx tsc -b --noEmit && cd ..

# 前端建置
cd frontend && npx vite build && cd ..

# 後端啟動測試（Ctrl+C 停止）
python backend/main.py --port 8000
# 瀏覽器開啟 http://127.0.0.1:8000/api/health 應回傳 {"status":"healthy","version":"4.0.0"}
```

---

## 4. 開發模式

### 方式 A：完整開發模式（三個終端機）

適合前端開發，支援 HMR 熱更新：

```bash
# 終端機 1 — FastAPI 後端
.venv\Scripts\activate
python backend/main.py --port 8000

# 終端機 2 — Vite Dev Server（前端 HMR）
cd frontend
npm run dev
# 啟動於 http://127.0.0.1:3000

# 終端機 3 — Electron Shell
set DUAT_ENV=development&& electron .
# Electron 會載入 Vite dev server
```

### 方式 B：簡易開發模式（單一終端機）

適合後端開發或快速測試，使用已構建的前端：

```bash
# 先確保前端已構建
cd frontend && npx vite build && cd ..

# 啟動 Electron（自動啟動 FastAPI sidecar + 載入已構建前端）
npm run dev
```

> 注意：`npm run dev` 會自動偵測 Vite dev server，連不上則 fallback 至 `frontend/dist/`。

### 方式 C：僅後端開發

不需要 Electron，直接用瀏覽器測試 API：

```bash
.venv\Scripts\activate
python backend/main.py --port 8000
# 用 Postman 或 curl 測試 http://127.0.0.1:8000/api/*
```

---

## 5. 專案結構

```
DUAT-Project-Managment/
├── electron/                # Electron 主進程
│   ├── main.js              # 視窗管理 + Sidecar 生命週期
│   ├── preload.js           # IPC 橋接 (window.electronAPI)
│   ├── sidecar.js           # FastAPI 進程管理
│   └── loading.html         # 載入畫面
├── frontend/                # React SPA (TypeScript + Vite)
│   ├── src/
│   │   ├── components/      # Layout, Sidebar, Charts, Tables
│   │   ├── pages/           # 7 個頁面
│   │   ├── lib/             # api.ts, store.ts, i18n.ts, types.ts
│   │   └── App.tsx          # 路由設定
│   └── dist/                # Vite 建置輸出（git ignored）
├── backend/                 # FastAPI REST API
│   ├── main.py              # 入口 + CORS + 路由註冊
│   ├── services.py          # 共享狀態管理（單例 registry）
│   └── routers/             # 9 個 API router（38 端點）
├── analysis/                # 5 個分析模組
├── parsers/                 # DOCX + 人力解析器
├── config.py                # JSON 設定讀寫
├── utils/                   # Excel 匯出工具
├── tests/                   # pytest 測試（365+ tests）
├── docs/                    # 文件
├── scripts/                 # 建置腳本
├── package.json             # Electron + 根目錄 scripts
├── requirements.txt         # Python 生產依賴
└── requirements-dev.txt     # Python 開發依賴
```

---

## 6. 常用指令

| 指令 | 說明 |
|------|------|
| `pytest tests/` | 執行全部後端測試 |
| `pytest tests/test_dashboard_api.py -v` | 執行 Dashboard API 測試 |
| `pytest tests/ --cov --cov-report=term-missing` | 測試 + 覆蓋率報告 |
| `cd frontend && npm run test` | 前端單元測試 |
| `cd frontend && npx tsc -b --noEmit` | TypeScript 型別檢查 |
| `cd frontend && npx vite build` | 前端建置 |
| `npm run build:all` | 完整建置（前端 + 後端 + Electron） |
| `npm run test:all` | 全部測試（後端 + 前端 + Electron） |

---

## 7. 建置可攜式 .exe

```bash
# 1. 建置前端
npm run frontend:build

# 2. 建置後端（PyInstaller）
.venv\Scripts\activate
npm run backend:build

# 3. 打包 Electron
npm run electron:build

# 輸出：build/win-unpacked/MTR DUAT.exe
```

---

## 8. 目前開發狀態

| 階段 | 狀態 | 進度 |
|------|------|------|
| Phase 0 基礎建設 | DONE | 100% |
| Phase 1 後端完善 | DONE | 100% |
| Phase 2 前端開發 | DONE | 100% |
| Phase 3 Electron 整合 | DONE | 100% |
| Phase 4 打包與測試 | IN PROGRESS | 60% |

### 待完成項目（Phase 4B）

- [ ] 在乾淨 Windows VM 上驗證無 Python/Node.js 環境啟動
- [ ] SharePoint 同步資料夾讀取測試
- [ ] 設定檔持久化驗證（關閉重開）
- [ ] UAT 使用者驗收測試（74 項，見 `docs/uat-test-plan.md`）

### 已修復 Bug

| Bug | 修復檔案 |
|-----|----------|
| 語言切換 zh/en 無效 | `Sidebar.tsx`, `Layout.tsx` |
| `npm run dev` 白屏 | `electron/main.js` |
| Dashboard API 404 | `frontend/src/lib/api.ts` |

---

## 9. 關鍵文件索引

| 文件 | 路徑 | 說明 |
|------|------|------|
| 系統架構 | `docs/architecture.md` | 四層架構、API 端點目錄（38 端點） |
| 重建計劃 | `docs/reconstruction-plan.md` | 完整開發計劃 + 代碼審查 |
| 產品需求 | `docs/prd.md` | 13 個 Epic、驗收標準 |
| 進度追蹤 | `docs/todolist.md` | 任務清單 + Bug 追蹤 |
| E2E 測試 | `docs/e2e-test-plan.md` | 16 個端對端測試場景 |
| UAT 測試 | `docs/uat-test-plan.md` | 74 個使用者驗收測試項目 |

---

## 10. 注意事項

1. Python 虛擬環境必須啟用（`.venv\Scripts\activate`）才能執行後端
2. 前端修改後需重新 `npx vite build` 才會反映在 Electron 簡易模式中
3. 後端 API port 在生產模式下是動態分配的，開發模式固定為 8000
4. 所有 API 通訊走 `127.0.0.1`（不走 `localhost`，避免企業防火牆問題）
5. 設定檔 `mtr_duat_config.json` 在 `.gitignore` 中，不會進入版本控制
6. `build/` 和 `backend_dist/` 目錄是建置輸出，已被 gitignore 排除
