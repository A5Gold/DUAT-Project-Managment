# MTR PS-OHLR DUAT - 每日更新分析工具

**版本**: 4.0.0 | **架構**: Electron + React SPA + FastAPI Sidecar

MTR 電力系統架空線更新（PS-OHLR）團隊的桌面分析工具。解析每日報告 DOCX 檔案，匯總項目交付數據，提供儀表板、滯後分析、績效追蹤、S-Curve、關鍵字搜尋及人力分析功能。

---

## 功能概覽

| 功能 | 說明 |
|------|------|
| DOCX 解析 | 自動掃描資料夾，解析每日報告中的藍色文字、項目代碼、鐵路線 |
| 儀表板 | 統計卡片 + 6 種圖表（每週/每月趨勢、專案/關鍵字/路線分佈） |
| 滯後分析 | 上傳 Project Master，計算 NTH Lag/Lead，5 級狀態分類 |
| 績效追蹤 | 每週/累計圖表、達成率、恢復路徑計算 |
| S-Curve | 目標 vs 實際累計曲線、Excel 匯出 |
| 關鍵字搜尋 | 在 DOCX 檔案中搜尋指定關鍵字 |
| 人力分析 | KPI、角色頻率、團隊分佈分析 |
| 國際化 | 中文 / English 即時切換 |
| 可攜式 | 打包為 .exe，無需安裝 Python 或 Node.js |

---

## 系統架構

### 四層架構總覽

```mermaid
graph TB
    subgraph Presentation["展示層"]
        React["React 19 SPA"]
        Charts["Chart.js 圖表"]
        Tailwind["Tailwind CSS"]
        Zustand["Zustand 狀態管理"]
    end

    subgraph Application["應用層"]
        Electron["Electron 33 主進程"]
        IPC["IPC 通訊"]
        Sidecar["Sidecar 生命週期管理"]
    end

    subgraph Business["業務邏輯層"]
        FastAPI["FastAPI REST API"]
        Routers["9 個 Router / 38 端點"]
        Analysis["5 個分析模組"]
        Parsers["2 個解析器"]
    end

    subgraph Data["資料層"]
        DOCX["DOCX 每日報告"]
        Excel["Project Master Excel"]
        JSON["JSON 設定檔"]
        Export["匯出 Excel 報告"]
    end

    React -->|HTTP REST| FastAPI
    React -->|Electron IPC| Electron
    Electron -->|spawn / kill| Sidecar
    Sidecar -->|管理| FastAPI
    FastAPI --> Routers
    Routers --> Analysis
    Routers --> Parsers
    Parsers -->|讀取| DOCX
    Analysis -->|讀取| Excel
    Analysis -->|寫入| Export
    FastAPI -->|讀寫| JSON
```

### Electron + Sidecar 啟動流程

```mermaid
sequenceDiagram
    participant User as 使用者
    participant E as Electron 主進程
    participant S as Sidecar Manager
    participant B as FastAPI 後端
    participant R as React SPA

    User->>E: 啟動應用程式
    E->>S: findFreePort()
    S-->>E: 回傳可用 port
    E->>S: spawnBackend(port)
    S->>B: python backend/main.py --port N

    loop 健康檢查（每 500ms，最多 30s）
        S->>B: GET /api/health
        B-->>S: 200 OK / 無回應
    end

    S-->>E: 後端就緒
    E->>R: 載入 React SPA
    R->>B: setPort(N) → 開始 API 通訊

    User->>E: 關閉視窗
    E->>S: killBackend()
    S->>B: SIGTERM
    E->>E: app.quit()
```

### IPC 通訊架構

```mermaid
graph LR
    subgraph Renderer["渲染進程（React SPA）"]
        API["window.electronAPI"]
    end

    subgraph Preload["Preload Script（Context Bridge）"]
        P1["getBackendPort()"]
        P2["openDirectory()"]
        P3["openFile()"]
        P4["onBackendReady()"]
        P5["onBackendError()"]
        P6["appQuit()"]
        P7["retrySidecar()"]
    end

    subgraph Main["主進程"]
        H1["dialog:openDirectory"]
        H2["dialog:openFile"]
        H3["sidecar:getPort"]
        H4["sidecar:retry"]
        H5["app:quit"]
    end

    API --> Preload
    Preload -->|ipcRenderer.invoke| Main
    Main -->|ipcMain.handle| Preload
```

---

## 重建歷程

本專案從 Python Flet + FastAPI 單體架構，重建為 Electron + React + FastAPI 混合桌面應用。

```mermaid
graph LR
    subgraph Before["重建前（v2.x）"]
        Flet["Python Flet UI"]
        FA1["FastAPI 後端"]
        Mono["單體 Python 應用"]
    end

    subgraph After["重建後（v4.0）"]
        E2["Electron Shell"]
        R2["React SPA"]
        FA2["FastAPI Sidecar"]
        Pkg["可攜式 .exe"]
    end

    Before -->|"Phase 0-3 重建"| After

    style Before fill:#fee,stroke:#c33
    style After fill:#efe,stroke:#3c3
```

### 重建階段

| 階段 | 內容 | 關鍵變化 |
|------|------|----------|
| Phase 0 | 基礎建設 | 建立 Electron Shell、Sidecar Manager、Preload Script |
| Phase 1 | 後端完善 | 重新開發 docx_parser、manpower_parser、config、excel_export |
| Phase 2 | 前端開發 | 從零建立 React SPA（7 頁面 + Zustand + i18n） |
| Phase 3 | Electron 整合 | IPC 通訊、動態 port、視窗管理、HMR 開發模式 |
| Phase 4 | 打包與測試 | PyInstaller + electron-builder → 可攜式 .exe |

### 重建前後對比

```mermaid
graph TB
    subgraph Old["舊架構"]
        direction TB
        O1["Python Flet UI<br/>（桌面渲染）"]
        O2["FastAPI 後端<br/>（同進程）"]
        O3["tkinter 檔案對話框"]
        O4["單一 Python 進程"]
    end

    subgraph New["新架構"]
        direction TB
        N1["React SPA<br/>（Chromium 渲染）"]
        N2["FastAPI Sidecar<br/>（獨立子進程）"]
        N3["Electron 原生對話框"]
        N4["多進程架構<br/>（主進程 + 渲染 + Sidecar）"]
    end

    O1 -.->|替換| N1
    O2 -.->|分離| N2
    O3 -.->|替換| N3
    O4 -.->|升級| N4
```

---

## 核心模組詳解

### 模組互動關係

```mermaid
graph TB
    subgraph FE["前端 React SPA"]
        Pages["7 個頁面"]
        Store["Zustand Store"]
        ApiClient["API Client"]
    end

    subgraph BE["後端 FastAPI"]
        Services["services.py<br/>（Singleton 註冊中心）"]
        R1["parse router"]
        R2["dashboard router"]
        R3["lag router"]
        R4["performance router"]
        R5["scurve router"]
        R6["manpower router"]
        R7["export router"]
    end

    subgraph Core["核心模組"]
        P1["DailyReportParser"]
        P2["ManpowerParser"]
        A1["DashboardAnalyzer"]
        A2["LagAnalyzer"]
        A3["PerformanceAnalyzer"]
        A4["SCurveGenerator"]
        A5["ManpowerAnalyzer"]
        U1["ExcelExport"]
        C1["Config"]
    end

    ApiClient -->|HTTP| R1 & R2 & R3 & R4 & R5 & R6 & R7
    R1 --> P1 & P2
    R2 --> A1
    R3 --> A2
    R4 --> A3
    R5 --> A4
    R6 --> A5
    R7 --> U1
    Services -->|管理| A1 & A2 & A3 & A4
    P1 -->|解析結果| A1
    A1 -->|Summary 數據| A2 & A3 & A4
```

---

## 演算法邏輯

### 1. DOCX 藍色文字偵測

解析器掃描 DOCX 表格中的每個儲存格，透過 RGB 色值判斷是否為藍色文字，從而識別工作類型關鍵字。

```mermaid
flowchart TD
    A["掃描 DOCX 表格"] --> B["逐列讀取儲存格"]
    B --> C{"檢查文字 RGB 色值"}
    C -->|"B >= 0x80 且<br/>R < 0x80 且<br/>G < 0x80"| D["判定為藍色文字"]
    C -->|不符合| E["跳過"]
    D --> F{"是否為夜班列？"}
    F -->|是| G["建立記錄<br/>Qty = 0"]
    F -->|否| H["提取項目代碼<br/>regex: C####"]
    H --> I["提取鐵路線代碼<br/>regex: KTL|TCL|AEL..."]
    I --> J["提取數量"]
    J --> K["建立完整記錄"]
    K --> L["輸出: FullDate, Project,<br/>Qty Delivered, Week, Year, Line"]
```

**檔名解析規則**：`PS-OHLR_DUAT_Daily Report_WK##_YYYY.docx` → 提取週數與年份

### 2. NTH Lag/Lead 滯後分析演算法

核心公式計算每個項目的進度偏差，並以 5 級狀態分類。

```mermaid
flowchart TD
    A["載入 Project Master Excel"] --> B["逐項目計算"]
    B --> C["已過天數 = today - start_date"]
    C --> D["目標進度% = 已過天數 / 總天數 × 100"]
    D --> E["目標累計數量 = 目標進度% × target_qty / 100"]
    E --> F["實際數量 = Dashboard Summary 中的 Qty"]
    F --> G["NTH Lag = (實際 - 目標累計) / 生產力"]
    G --> H{"Lag 值分類"}

    H -->|"lag <= -10"| I["URGENT 🔴"]
    H -->|"-10 < lag <= -5"| J["BEHIND 🟠"]
    H -->|"-5 < lag < 0"| K["SLIGHT LAG 🟡"]
    H -->|"0 <= lag < 5"| L["ON TRACK 🟢"]
    H -->|"lag >= 5"| M["AHEAD 🔵"]

    style I fill:#f66,stroke:#c33
    style J fill:#fa0,stroke:#c70
    style K fill:#ff0,stroke:#cc0
    style L fill:#6f6,stroke:#3c3
    style M fill:#6af,stroke:#38c
```

**公式摘要**：

```
elapsed_days    = (today - start_date).days
target_progress = (elapsed_days / total_days) × 100
target_qty_now  = target_progress × target_qty / 100
NTH_Lag_Lead    = (actual_qty - target_qty_now) / productivity
```

### 3. 績效追蹤演算法

```mermaid
flowchart TD
    A["載入每週交付數據"] --> B["計算每週生產力"]
    B --> C["weekly_productivity = Qty / NTH_Count"]
    C --> D["達成率 = 達標週數 / 總週數 × 100%"]
    D --> E["當前步伐 = 最近 12 週平均生產力"]
    E --> F{"當前步伐 >= 目標？"}
    F -->|是| G["進度正常"]
    F -->|否| H["計算恢復路徑"]
    H --> I["所需週產量 =<br/>(目標總量 - 已完成) / 剩餘週數"]

    subgraph Charts["圖表輸出（base64 PNG）"]
        J["每週績效長條圖<br/>綠=達標 / 紅=未達"]
        K["累計進度圖<br/>計劃線 + 實際線 + 恢復路徑"]
    end

    G --> Charts
    I --> Charts
```

### 4. S-Curve 累計曲線演算法

```mermaid
flowchart LR
    A["設定起止週期"] --> B["計算總週數<br/>（處理 ISO 52/53 週）"]
    B --> C["生成週標籤<br/>YYYY-Wnn"]
    C --> D["累計目標線<br/>target × (i+1) / total_weeks"]
    D --> E["累計實際線<br/>逐週加總實際交付"]
    E --> F["進度% = 實際累計 / 目標總量 × 100"]
    F --> G["輸出 S-Curve 圖表"]

    subgraph Output["輸出格式"]
        G1["JSON: week_labels, cum_target, cum_actual, progress%"]
        G2["Excel: 數據表 + 嵌入圖表"]
    end

    G --> Output
```

### 5. 人力分析演算法

```mermaid
flowchart TD
    A["解析人力班次數據"] --> B["每日人數統計"]
    B --> C["具名人員 + 學徒 + 臨時工 + 團隊"]

    A --> D["工作類型分類"]
    D --> E{"關鍵字優先級匹配"}
    E -->|"CP(P) 存在"| F["Possession 工作"]
    E -->|"PA work"| G["PA 工作"]
    E -->|"SPA work"| H["SPA 工作"]
    E -->|"其他"| I["一般工作"]

    A --> J["EPIC 角色提取"]
    J --> K["CP(P), CP(T), AP(E),<br/>SPC, HSM, NP"]
    K --> L["角色頻率矩陣<br/>人員 × 角色"]

    A --> M["團隊分佈"]
    M --> N["S2/S3/S4/S5<br/>每週配置統計"]

    subgraph KPI["KPI 輸出"]
        O1["總工作數"]
        O2["平均工人數"]
        O3["不重複人員數"]
        O4["最高頻角色持有者"]
    end

    B & D & J & M --> KPI
```

### 6. 儀表板分析流程

```mermaid
flowchart TD
    A["原始 DOCX 記錄"] --> B["aggregate_records()"]
    B --> C["清洗 DataFrame<br/>提取 Day, Date, Week, Month"]
    C --> D["calculate_summary()"]
    D --> E["每項目統計<br/>Total NTH, Qty, Avg/Week"]

    C --> F["get_weekly_trend()"]
    F --> G["按關鍵字分類<br/>CBM, CM, PA, HLM, Provide"]
    G --> H["最近 N 週趨勢"]

    C --> I["get_monthly_trend()"]
    I --> J["ISO 週轉月份<br/>最近 N 月趨勢"]

    C --> K["get_nth_pivot_by_week()"]
    K --> L["樞紐分析表<br/>YearWeek × Project"]

    subgraph Output["儀表板輸出"]
        E
        H
        J
        L
    end
```

---

## 資料流程

### 完整資料處理管線

```mermaid
sequenceDiagram
    participant U as 使用者
    participant FE as React SPA
    participant BE as FastAPI
    participant P as DailyReportParser
    participant DA as DashboardAnalyzer
    participant LA as LagAnalyzer
    participant PA as PerformanceAnalyzer
    participant SC as SCurveGenerator
    participant EX as ExcelExport

    Note over U,EX: 階段一：資料匯入
    U->>FE: 選擇 DOCX 資料夾
    FE->>BE: POST /api/parse/folder
    BE->>P: 背景解析任務
    loop 進度輪詢（每 1 秒）
        FE->>BE: GET /api/parse/progress
        BE-->>FE: {current_file, percentage}
    end
    P-->>BE: 解析完成（records[]）
    FE->>BE: GET /api/parse/results

    Note over U,EX: 階段二：儀表板分析
    FE->>BE: POST /api/dashboard/analyze {records}
    BE->>DA: load_from_records()
    DA-->>BE: stats, trends, pivot

    Note over U,EX: 階段三：進階分析
    U->>FE: 上傳 Project Master Excel
    FE->>BE: POST /api/lag/load-master {file}
    BE->>LA: load_project_master()
    LA->>DA: 讀取 summary（自動匹配生產力）
    FE->>BE: POST /api/lag/calculate
    LA-->>BE: lag/lead 結果

    FE->>BE: POST /api/performance/analyze
    BE->>PA: set_data() + analyze()
    PA-->>BE: 績效圖表（base64 PNG）

    FE->>BE: POST /api/scurve/calculate
    BE->>SC: generate()
    SC-->>BE: S-Curve 數據

    Note over U,EX: 階段四：匯出
    FE->>BE: POST /api/export/dashboard
    BE->>EX: create_dashboard_excel()
    EX-->>FE: FileResponse（Excel 下載）
```

### 設定檔路徑策略

```mermaid
flowchart TD
    A["啟動應用"] --> B{"DUAT_CONFIG_PATH<br/>環境變數存在？"}
    B -->|是| C["使用環境變數路徑"]
    B -->|否| D{"是否為打包環境？<br/>（sys.frozen）"}
    D -->|是| E["exe 同目錄<br/>mtr_duat_config.json"]
    D -->|否| F["工作目錄<br/>./mtr_duat_config.json"]
```

---

## 專案結構

```
├── electron/               # Electron 主進程
│   ├── main.js             # 視窗建立 + IPC Handler + Sidecar 啟動
│   ├── sidecar.js          # Sidecar Manager（port 分配、健康檢查、進程管理）
│   └── preload.js          # Context Bridge（安全暴露 API 給渲染進程）
├── frontend/               # React SPA（TypeScript + Vite + Tailwind）
│   └── src/
│       ├── components/     # 共用元件
│       │   ├── Layout.tsx          # 主佈局
│       │   ├── Sidebar.tsx         # 導航選單
│       │   ├── charts/            # BarChart, LineChart, PieChart, SCurveChart
│       │   └── tables/            # DataTable, PivotTable
│       ├── pages/          # 7 個頁面
│       │   ├── HomePage.tsx        # 資料夾選擇 + 解析
│       │   ├── DashboardPage.tsx   # 統計 + 6 種圖表
│       │   ├── LagAnalysisPage.tsx # Master 上傳 + 滯後結果
│       │   ├── PerformancePage.tsx # 每週 + 累計圖表
│       │   ├── KeywordSearchPage.tsx
│       │   └── ManpowerPage.tsx    # KPI + 角色分析
│       └── lib/            # 核心工具
│           ├── api.ts              # HTTP Client（動態 port）
│           ├── store.ts            # Zustand 全域狀態
│           ├── i18n.ts             # 中英文翻譯
│           └── types.ts            # TypeScript 介面定義
├── backend/                # FastAPI REST API
│   ├── main.py             # 入口 + CORS + 路由註冊 + --port 參數
│   ├── services.py         # Singleton 註冊中心（5 個分析器實例）
│   └── routers/            # 9 個 API Router
│       ├── config.py       # 設定 CRUD + 重置
│       ├── parse.py        # DOCX 解析 + 進度輪詢
│       ├── dashboard.py    # 統計 + 趨勢 + 分佈 + 樞紐分析
│       ├── lag.py          # Master 上傳 + Lag/Lead 計算
│       ├── performance.py  # 績效分析 + 圖表生成
│       ├── scurve.py       # S-Curve 計算 + Excel 匯出
│       ├── export.py       # Dashboard/Lag Excel 匯出
│       ├── keyword.py      # 全文搜尋
│       └── manpower.py     # 人力掃描 + 分析 + 匯出
├── analysis/               # 5 個分析模組
│   ├── dashboard.py        # DashboardAnalyzer（聚合、摘要、趨勢、樞紐）
│   ├── lag_analysis.py     # LagAnalyzer（Lag/Lead 計算、5 級分類）
│   ├── performance.py      # PerformanceAnalyzer（生產力、達成率、恢復路徑）
│   ├── scurve.py           # SCurveGenerator（累計曲線、ISO 週處理）
│   └── manpower.py         # ManpowerAnalyzer（KPI、角色、團隊、工作分類）
├── parsers/                # 解析器
│   ├── docx_parser.py      # DailyReportParser（藍色文字偵測、記錄提取）
│   └── manpower_parser.py  # ManpowerParser（班次、角色、團隊解析）
├── config.py               # JSON 設定讀寫（可攜式路徑策略）
├── utils/
│   └── excel_export.py     # Excel 匯出工具（多表、自動欄寬）
├── tests/                  # pytest 測試（365+ tests, 92%+ 覆蓋率）
├── docs/                   # 技術文件
└── scripts/                # 建置腳本
```

---

## 技術棧

| 層級 | 技術 | 版本 |
|------|------|------|
| 展示層 | React + Tailwind CSS + Chart.js + Zustand | 19 / 4.x / 4.5 / 4.5 |
| 應用層 | Electron + electron-builder | 33 / 25 |
| 業務邏輯層 | FastAPI + Uvicorn + pandas + numpy + matplotlib | 3.0 / 2.2 / 1.26 / 3.9 |
| 解析層 | python-docx + openpyxl | 1.1 / 3.1 |
| 建置工具 | Vite + PyInstaller + electron-builder | 7 / 6 / 25 |

---

## API 端點（38 個）

| 路由 | 端點數 | 說明 |
|------|--------|------|
| `/api/health` | 2 | 健康檢查 |
| `/api/config` | 4 | 設定管理（CRUD + 重置） |
| `/api/parse` | 5 | DOCX 解析（啟動、進度、結果、取消） |
| `/api/dashboard` | 12 | 儀表板（統計、趨勢、分佈、樞紐、原始數據） |
| `/api/lag` | 6 | 滯後分析（Master 上傳、計算、結果、狀態圖例） |
| `/api/performance` | 8 | 績效（每週分析、累計圖表、恢復路徑） |
| `/api/scurve` | 4 | S-Curve（計算、圖表、Excel 匯出） |
| `/api/export` | 4 | Excel 匯出（儀表板、滯後報告、檔案下載） |
| `/api/keyword` | 1 | 關鍵字全文搜尋 |
| `/api/manpower` | 3 | 人力分析（掃描、KPI、Excel 匯出） |

---

## 快速開始

### 前置需求

- Python 3.12+
- Node.js 20.x LTS
- Git

### 安裝

```bash
git clone https://github.com/A5Gold/DUAT-Project-Managment.git
cd DUAT-Project-Managment

# Python 環境
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Node 依賴
npm install
cd frontend && npm install && cd ..
```

### 開發模式

```bash
# 方式 A：完整開發（三個終端機，支援 HMR）
python backend/main.py --port 8000     # 終端機 1
cd frontend && npm run dev             # 終端機 2
set DUAT_ENV=development&& electron .  # 終端機 3

# 方式 B：簡易模式（單一終端機，使用已構建前端）
cd frontend && npx vite build && cd ..
npm run dev
```

---

## 指令參考

| 指令 | 說明 |
|------|------|
| `npm run dev` | 啟動 Electron（開發模式） |
| `npm run dev:backend` | 啟動 FastAPI 後端（port 8000） |
| `npm run dev:frontend` | 啟動 Vite Dev Server（port 3000） |
| `npm run frontend:build` | 建置前端 |
| `npm run backend:build` | PyInstaller 打包後端 |
| `npm run electron:build` | electron-builder 打包 |
| `npm run build` | 前端建置 + Electron 打包 |
| `npm run build:all` | 前端 + 後端 + Electron 完整建置 |
| `npm run test:backend` | 後端測試 + 覆蓋率 |
| `npm run test:frontend` | 前端單元測試 |
| `npm run test:electron` | Electron 測試 |
| `npm run test:all` | 全部測試 |

---

## 測試

```bash
# 後端測試（365+ tests, 92%+ 覆蓋率）
pytest tests/ --cov --cov-report=term-missing

# 前端測試
cd frontend && npm run test

# 全部測試
npm run test:all
```

---

## 建置可攜式 .exe

```mermaid
flowchart LR
    A["npm run frontend:build"] -->|"Vite 建置"| B["frontend/dist/"]
    C["npm run backend:build"] -->|"PyInstaller"| D["backend_dist/"]
    B & D --> E["npm run electron:build"]
    E -->|"electron-builder"| F["build/win-unpacked/<br/>MTR DUAT.exe"]

    style F fill:#efe,stroke:#3c3
```

```bash
npm run frontend:build    # 1. 建置前端
npm run backend:build     # 2. PyInstaller 打包後端
npm run electron:build    # 3. Electron 打包
# 輸出：build/win-unpacked/MTR DUAT.exe
```

---

## 環境變數

| 變數 | 說明 | 開發預設值 | 生產值 |
|------|------|------------|--------|
| `DUAT_ENV` | 環境標識 | `development` | `production` |
| `DUAT_BACKEND_PORT` | 後端固定 port | `8000` | 動態分配 |
| `DUAT_LOG_LEVEL` | 日誌級別 | `DEBUG` | `WARNING` |
| `DUAT_CONFIG_PATH` | 設定檔路徑 | `./mtr_duat_config.json` | 與 .exe 同目錄 |

---

## 文件

| 文件 | 說明 |
|------|------|
| [architecture.md](docs/architecture.md) | 系統架構 + API 端點目錄 |
| [reconstruction-plan.md](docs/reconstruction-plan.md) | 完整重建計劃 |
| [prd.md](docs/prd.md) | 產品需求（13 Epic） |
| [todolist.md](docs/todolist.md) | 進度追蹤 + Bug 追蹤 |
| [dev-setup-guide.md](docs/dev-setup-guide.md) | 開發環境設置指南 |
| [e2e-test-plan.md](docs/e2e-test-plan.md) | E2E 測試計劃 |
| [uat-test-plan.md](docs/uat-test-plan.md) | UAT 驗收測試計劃 |

---

## 開發狀態

| 階段 | 狀態 | 進度 |
|------|------|------|
| Phase 0 基礎建設 | DONE | 100% |
| Phase 1 後端完善 | DONE | 100% |
| Phase 2 前端開發 | DONE | 100% |
| Phase 3 Electron 整合 | DONE | 100% |
| Phase 4 打包與測試 | IN PROGRESS | 60% |

---

## 授權

UNLICENSED - MTR 內部使用
