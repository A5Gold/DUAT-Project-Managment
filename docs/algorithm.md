# 演算法邏輯文件

## MTR PS-OHLR DUAT - 每日更新分析工具

本文件描述程式碼中每個函式、元件和模組的演算法邏輯，並以 Mermaid 流程圖輔助說明。此文件對未來重建（Electron + Python + React + API + SQLite）至關重要。

---

## 1. 整體數據處理流程

```mermaid
graph TD
    DOCX["DOCX 每日報告檔案"] -->|"DailyReportParser"| Records["原始記錄 List of Dict"]
    Records -->|"POST /api/dashboard/analyze"| Agg["aggregate_records"]
    Agg --> DF["清洗後 DataFrame"]
    DF --> Summary["calculate_summary"]
    DF --> Weekly["get_weekly_trend"]
    DF --> Monthly["get_monthly_trend"]
    DF --> ProjDist["get_project_distribution"]
    DF --> KwDist["get_keyword_distribution"]
    DF --> Pivot["get_nth_pivot_by_week"]

    DF -->|"set-data"| Perf["PerformanceAnalyzer"]
    DF -->|"set-data"| SCurve["SCurveGenerator"]
    Summary -->|"productivity 匹配"| Lag["LagAnalyzer"]

    DOCX -->|"ManpowerParser"| MPRecords["人力記錄"]
    MPRecords --> MPA["ManpowerAnalyzer"]

    DOCX -->|"python-docx"| KW["關鍵字搜尋"]
```

---

## 2. 分析模組 (`analysis/`)

### 2.1 儀表板分析 (`analysis/dashboard.py`)

#### `aggregate_records(records) -> DataFrame`

目的：將原始解析記錄轉換為清洗後的 DataFrame。

```mermaid
graph TD
    A["輸入: List of Dict"] --> B["轉換為 pandas DataFrame"]
    B --> C["用 regex ^[A-Za-z]{3} 提取 Day"]
    C --> D["用 regex 去除日期前綴提取 Date"]
    D --> E["用 regex 提取數字 Week"]
    E --> F["組合 Date + Year 解析 DateObj"]
    F --> G["從 DateObj 衍生 Month YYYY-MM"]
    G --> H["輸出: 清洗後 DataFrame"]
```

演算法步驟：
1. 將 list of dicts 轉為 pandas DataFrame
2. 用 regex `^([A-Za-z]{3})` 從 `FullDate` 提取 `Day`（三字母縮寫）
3. 用 regex 去除 `FullDate` 的日期前綴得到 `Date`
4. 用 regex `(\d+)` 從 Week 字串提取數字
5. 組合 `Date + '/' + Year` 以 `%d/%m/%Y` 格式解析為 `DateObj`
6. 從 `DateObj` 衍生 `Month`（`YYYY-MM` 格式）

輸入欄位：FullDate, Project, Qty Delivered, Week, Year
輸出新增欄位：Day, Date, DateObj, Month

---

#### `calculate_summary(df, current_week, current_month) -> DataFrame`

目的：按項目計算摘要統計。

```mermaid
graph TD
    A["輸入: 清洗後 DataFrame"] --> B["預設 current_week = max Week"]
    B --> C["預設 current_month = datetime.now.month"]
    C --> D["刪除 DateObj/Month/Week 為 NaN 的列"]
    D --> E["GroupBy Project 計算 Total NTH = COUNT"]
    D --> F["GroupBy Project 計算 Qty Delivered = SUM"]
    E --> G["Merge NTH 與 Qty"]
    F --> G
    G --> H["計算衍生指標"]
    H --> I["按 Qty Delivered 降序排列"]
    I --> J["插入 Rank 欄位"]
    J --> K["輸出: Summary DataFrame"]
```

衍生指標公式：
- `Qty per NTH` = Qty Delivered / Total NTH
- `Avg Qty per Week` = Qty Delivered / current_week
- `Avg Qty per Month` = Qty Delivered / current_month
- `Avg NTH per Week` = Total NTH / current_week
- `Avg NTH per Month` = Total NTH / current_month

---

#### `get_weekly_trend(df, weeks=12) -> Tuple[List, Dict]`

目的：取得按 Projects vs Jobs 分類的每週 NTH 趨勢。

```mermaid
graph TD
    A["輸入: DataFrame"] --> B["建立 YearWeek 欄位 YYYY-Wnn"]
    B --> C["分類每列"]
    C --> D{"Project 包含<br/>CBM/CM/PA work/HLM/Provide?"}
    D -->|是| E["分類為 Jobs"]
    D -->|否| F["分類為 Projects"]
    E --> G["取最近 N 週"]
    F --> G
    G --> H["按 YearWeek GroupBy 計算每類 NTH"]
    H --> I["輸出: week_labels, category_data"]
```

分類關鍵字（不區分大小寫）：`CBM`, `CM`, `PA work`, `HLM`, `Provide`

---

#### `get_monthly_trend(df, months=6) -> Tuple[List, List]`

目的：按月份匯總 NTH 趨勢。

演算法：
1. 將 Week 轉換為近似月份：`Month = ((Week - 1) // 4.33 + 1).clip(1, 12)`
2. 建立 `YearMonth`（`YYYY-MM`）
3. GroupBy YearMonth 計算 NTH 數量
4. 取最近 N 個月，按時間排序

---

#### `get_project_distribution(df) -> Dict[str, int]`

目的：按項目統計 NTH 分佈。

演算法：GroupBy Project 計算 size。將 `Provide` 重新命名為 `Provide manpower for switching`。

---

#### `get_keyword_distribution(df) -> Dict[str, int]`

目的：按工作關鍵字統計 NTH 分佈。

演算法：對每個關鍵字 `[CBM, CM, PA work, HLM, Provide]`，計算 Project 欄位包含該關鍵字的列數（不區分大小寫 `str.contains`）。

---

#### `get_nth_pivot_by_week(df) -> DataFrame`

目的：建立 NTH 樞紐分析表（週 x 項目）。

```mermaid
graph TD
    A["輸入: DataFrame"] --> B["建立 YearWeek 欄位"]
    B --> C["GroupBy YearWeek + Project 計算 size"]
    C --> D["Pivot: rows=YearWeek, columns=Project"]
    D --> E["NaN 填充為 0"]
    E --> F["按週排序"]
    F --> G["輸出: 樞紐分析表 DataFrame"]
```

---

#### `class DashboardAnalyzer`

目的：高層儀表板數據管理器（在 router 中作為全域單例使用）。

```mermaid
graph TD
    subgraph DashboardAnalyzer
        State["狀態: df, summary, last_updated, nth_trend"]
        LR["load_from_records"] --> AGG["aggregate_records"]
        AGG --> CS["calculate_summary"]
        CS --> NP["get_nth_pivot_by_week"]
        LE["load_from_excel"] --> ReadExcel["pd.read_excel 讀取各 Sheet"]
        GS["get_stats"] --> Stats["total_records, total_qty, unique_projects"]
        EX["export"] --> ExcelOut["export_dashboard_excel"]
    end
```

方法：
- `load_from_records(records, max_week)`: aggregate_records -> calculate_summary -> get_nth_pivot_by_week
- `load_from_excel(filepath)`: 讀取 Raw Data sheet，可選讀取 Summary 和 NTH Trend sheets
- `get_stats()`: 回傳 `{total_records, total_nth, total_qty, unique_projects, last_updated}`
- `export(output_path)`: 委派給 export_dashboard_excel

---

### 2.2 滯後/超前分析 (`analysis/lag_analysis.py`)

#### `get_status(nth_lag_lead) -> Tuple[str, str]`

目的：根據 NTH lag/lead 值分類項目狀態。

```mermaid
graph TD
    A["輸入: nth_lag_lead 數值"] --> B{"值 <= -10?"}
    B -->|是| C["URGENT 紅色"]
    B -->|否| D{"值 <= -5?"}
    D -->|是| E["BEHIND 橙色"]
    D -->|否| F{"值 < 0?"}
    F -->|是| G["SLIGHT LAG 黃色"]
    F -->|否| H{"值 < 5?"}
    H -->|是| I["ON TRACK 綠色"]
    H -->|否| J["AHEAD 藍色"]
```

閾值表：

| NTH Lag/Lead | 狀態 | 顏色 | 嚴重程度 |
|-------------|------|------|----------|
| <= -10 | URGENT | red | 危急 |
| <= -5 | BEHIND | orange | 高 |
| < 0 | SLIGHT LAG | yellow | 中 |
| < 5 | ON TRACK | green | 正常 |
| >= 5 | AHEAD | blue | 正面 |

---

#### `load_project_master(filepath) -> Tuple[DataFrame, Dict, Dict]`

目的：載入並解析 Project Master Excel 檔案。

```mermaid
graph TD
    A["輸入: Excel 檔案路徑"] --> B["pd.read_excel 讀取"]
    B --> C["不區分大小寫欄位映射"]
    C --> D["尋找 Project No 欄位"]
    C --> E["尋找 One Line Title 欄位"]
    C --> F["尋找 Start/End Date 欄位"]
    C --> G["尋找 Target Qty 欄位"]
    D --> H["遍歷每列提取數據"]
    E --> H
    F --> H
    G --> H
    H --> I["建立 project_master DataFrame"]
    H --> J["建立 project_descriptions Dict"]
    H --> K["建立 target_qty_map Dict"]
    I --> L["輸出: 三元組"]
    J --> L
    K --> L
```

欄位映射優先順序（不區分大小寫）：
- Project No: `project no` > `projectno` > `project number` > Column C (fallback)
- Description: `one line title`（最高優先） > `description` > `title` > `project title`
- Start Date: `start date` > `startdate`
- End Date: `finish date` > `end date` > `finishdate`
- Target Qty: `target quantity` > `target qty`

---

#### `calculate_nth_lag_lead(project_master, config, actual_qty_map) -> List[Dict]`

目的：使用線性插值計算所有項目的 NTH 滯後/超前。

```mermaid
graph TD
    A["遍歷每個項目"] --> B{"config.skip = True?"}
    B -->|是| SKIP["跳過"]
    B -->|否| C{"有效 target_qty?"}
    C -->|否| SKIP
    C -->|是| D["計算 total_days = End - Start"]
    D --> E["計算 elapsed_days = max 0 today - Start"]
    E --> F["target_progress% = min 100 elapsed/total * 100"]
    F --> G["target_qty_to_date = progress% / 100 * target_qty"]
    G --> H["actual_qty = actual_qty_map 查詢"]
    H --> I["qty_difference = actual - target_to_date"]
    I --> J["nth_lag_lead = qty_difference / productivity"]
    J --> K["get_status 分類狀態"]
    K --> L["加入結果列表"]
```

核心公式：
```
target_progress% = min(100, (today - start_date).days / (end_date - start_date).days * 100)
target_to_date = target_progress% / 100 * target_qty
nth_lag_lead = (actual_qty - target_to_date) / productivity
```

其中 `productivity` 預設為 3.0（Qty per NTH），可從儀表板 summary 自動匹配或由使用者手動輸入。

---

#### `class LagAnalyzer`

目的：高層滯後分析管理器。

```mermaid
graph TD
    subgraph LagAnalyzer
        LPM["load_project_master"] --> LoadExcel["讀取 Excel"]
        LoadExcel --> InitConfig["初始化每個項目 config"]
        InitConfig --> MatchProd["_match_productivity"]
        MatchProd --> ScanSummary["掃描 dashboard summary<br/>尋找 Qty per NTH"]
        Calc["calculate"] --> CalcNTH["calculate_nth_lag_lead"]
        CalcNTH --> StoreResults["儲存結果為 DataFrame"]
        Export["export"] --> ExportExcel["export_lag_report"]
    end
```

Productivity 來源優先順序：
1. `user_input` — 使用者手動輸入
2. `daily_report` — 從 dashboard summary 的 `Qty per NTH` 自動匹配
3. `default` — 預設值 3.0

---

### 2.3 S-Curve 生成 (`analysis/scurve.py`)

#### `calculate_scurve_data(df, project_code, target_qty, start_year, start_week, end_year, end_week)`

目的：計算特定項目的累計計劃 vs 實際進度數據。

```mermaid
graph TD
    A["輸入: DataFrame + 項目參數"] --> B["篩選 project_code 不區分大小寫"]
    B --> C["total_weeks = end_year - start_year * 52 + end_week - start_week"]
    C --> D["生成 week_labels 序列 YYYY-Wnn"]
    D --> E["weekly_target = target_qty / total_weeks"]
    E --> F["cumulative_target i = weekly_target * i+1"]
    F --> G["GroupBy YearWeek 計算實際 Qty"]
    G --> H["cumulative_actual = 逐週累加"]
    H --> I["progress% = last_actual / target_qty * 100"]
    I --> J["輸出: week_labels, cum_target, cum_actual, progress%"]
```

核心公式：
```
weekly_target = target_qty / total_weeks
cumulative_target[i] = weekly_target * (i + 1)
cumulative_actual[i] = cumulative_actual[i-1] + actual_qty_for_week[i]
progress% = cumulative_actual[-1] / target_qty * 100
```

週標籤生成邏輯：從 start_year/start_week 開始遞增，week > 52 時 rollover 至下一年 week 1。

---

#### `plot_scurve(...) -> Optional[str]`

目的：生成 S-Curve 圖表（base64 PNG 或檔案）。

視覺元素：
1. 目標線：藍色虛線，linewidth=2，alpha=0.7
2. 實際線：綠色實線，linewidth=2.5，圓形標記 size=4
3. 填充區域：超前為綠色（alpha=0.2），落後為紅色（alpha=0.2）
4. X 軸：每 N 個標籤顯示一個，N = max(1, total_labels // 12)

---

### 2.4 績效分析 (`analysis/performance.py`)

#### `calculate_performance_metrics(df, project_code, target_productivity=3.0) -> Dict`

目的：計算項目的每週生產力指標。

```mermaid
graph TD
    A["篩選 project_code"] --> B["GroupBy Year+Week 計算 SUM Qty"]
    B --> C["GroupBy Year+Week 計算 COUNT NTH"]
    C --> D["Merge Qty 與 NTH"]
    D --> E["Actual Productivity = Qty / NTH per week"]
    E --> F["按 Year Week 排序"]
    F --> G["weeks_met = count Actual >= target"]
    G --> H["success_rate = met / total * 100"]
    H --> I["current_pace = last 12 weeks SUM Qty / SUM NTH"]
    I --> J["avg_productivity = mean of all weekly values"]
```

核心公式：
```
actual_productivity_week = qty_delivered_week / nth_count_week
success_rate = weeks_met_target / total_weeks * 100
current_pace = sum(last_12_weeks_qty) / sum(last_12_weeks_nth)
```

---

#### `get_recovery_path(target_qty, actual_qty, remaining_weeks, current_productivity) -> Dict`

目的：計算達成目標所需的恢復路徑。

```mermaid
graph TD
    A["輸入: target, actual, remaining_weeks, pace"] --> B["remaining_qty = target - actual"]
    B --> C["required_weekly = remaining / weeks"]
    C --> D["required_productivity = required_weekly"]
    D --> E{"current_productivity >= required?"}
    E -->|是| F["on_track = True"]
    E -->|否| G["on_track = False"]
    B --> H["weeks_to_complete = remaining / current_pace"]
```

---

#### `plot_performance_chart(...) -> Optional[str]`

視覺元素：
1. 長條圖：達標為綠色，未達標為紅色（alpha=0.7）
2. 水平目標線：藍色虛線，linewidth=2
3. X 軸：每 N 個標籤顯示，N = max(1, total // 10)

---

#### `plot_cumulative_progress(...) -> Optional[str]`

演算法：
1. 篩選項目，GroupBy Year，SUM Qty Delivered，cumsum 計算實際累計
2. 線性目標：`yearly_target = target_qty / total_years`，累計 = yearly_target * (i+1)
3. 恢復路徑：`np.linspace` 從 last_actual_value 到 target_qty
4. 繪製：Plan（藍色虛線）、Actual（綠色實線+標記）、Recovery（紅色點線）

---

### 2.5 人力分析 (`analysis/manpower.py`)

#### `get_daily_headcount(records) -> List[Dict]`

目的：計算每日每班次的人數。

公式：
```
headcount = len(on_duty_names) + len(apprentices) + term_labour_count + sum(team_counts.values())
```

---

#### `get_team_distribution(records) -> Dict[str, Dict[str, int]]`

目的：按週匯總團隊（S2/S3/S4/S5）分配。

演算法：從所有 jobs 的 team_counts 中累加每個 team_id 的數量，按週分組，按週號排序。

---

#### `get_job_type_manpower(records) -> Dict[str, Dict]`

目的：計算每種工作類型的平均工人數和角色分佈。

```mermaid
graph TD
    A["遍歷所有 records 的 jobs"] --> B["按 job type 累加"]
    B --> C["total_jobs++"]
    B --> D["total_workers += job.total_workers"]
    B --> E["team_sums S2-S5 累加"]
    B --> F["role_sums CP_P/CP_T/AP_E/SPC/HSM/NP 累加"]
    C --> G["avg_workers = total_workers / total_jobs"]
    E --> H["avg_team_counts = team_sums / total_jobs"]
    F --> I["avg_roles = role_sums / total_jobs"]
```

---

#### `get_role_frequency(records) -> List[Dict]`

目的：統計每個人在所有工作中擔任各 EPIC 角色的頻率。

演算法：遍歷所有 jobs 的 roles，對每個角色（CP_P, CP_T, AP_E, SPC, HSM, NP）中的每個人名累加計數。按總分配次數降序排列。

---

#### `get_work_access_analysis(records) -> Dict[str, Dict]`

目的：按工作存取類型分析工作。

```mermaid
graph TD
    A["遍歷每個 job"] --> B{"job type = SPA work?"}
    B -->|是| C["分類: SPA work"]
    B -->|否| D{"job type = PA work?"}
    D -->|是| E["分類: PA work"]
    D -->|否| F{"有 CP_P 角色?"}
    F -->|是| G["分類: Possession"]
    F -->|否| H["分類: Other"]
    C --> I["累加 count, workers, AP, SPC, HSM"]
    E --> I
    G --> I
    H --> I
    I --> J["計算每類平均值"]
```

分類邏輯：
- `SPA work`：特殊行人通道工作
- `PA work`：行人通道工作，無工程列車
- `Possession`：有 CP(P) 角色 = 電氣隔離區域中的工程列車
- `Other`：不符合以上類別

---

#### `get_summary_kpis(records) -> Dict`

目的：計算頂層 KPI 摘要。

演算法：
1. `total_jobs` = 所有 records 中 jobs 的總數
2. `avg_workers_per_job` = total_workers / total_jobs
3. `unique_staff_count` = on_duty_names + apprentices + worker_names 的唯一人名數
4. `top_role_holder` = get_role_frequency 結果中排名第一的人

---

#### `export_manpower_excel(records, filepath) -> Path`

目的：匯出人力分析至格式化 Excel 工作簿。

匯出 Sheets：
1. Raw Data：24 欄（Year, Week, Date, Day, Shift, Job Type, Project Code, Description, Qty, Done By, Total Workers, S2-S5, EPIC, CP(P)-HSM, On Duty Count, Apprentices, Term Labour）
2. Job Type Summary：工作類型、總數、平均工人數、平均角色數
3. Role Frequency：人名 x 角色計數矩陣
4. Weekly Team Distribution：每週 S2/S3/S4/S5 分配

---

## 3. 後端模組 (`backend/`)

### 3.1 FastAPI 應用程式 (`backend/main.py`)

```mermaid
graph TD
    App["FastAPI App v3.0.0"] --> CORS["CORS Middleware<br/>origins: localhost:3000"]
    App --> R1["/api/config"]
    App --> R2["/api/parse"]
    App --> R3["/api/dashboard"]
    App --> R4["/api/lag"]
    App --> R5["/api/performance"]
    App --> R6["/api/scurve"]
    App --> R7["/api/export"]
    App --> R8["/api/keyword"]
    App --> R9["/api/manpower"]
    App --> Health["/ + /api/health"]
```

建立 FastAPI app v3.0.0，配置 CORS middleware（origins: localhost:3000, 127.0.0.1:3000），註冊 9 個 router 於 `/api/` 前綴下。健康檢查端點位於 `/` 和 `/api/health`。

### 3.2 設定路由 (`backend/routers/config.py`)

Browse 演算法（原生資料夾選擇）：
1. 建立暫存檔案用於結果和錯誤
2. 清理路徑（反斜線轉正斜線）
3. 生成 Python 腳本：設定 DPI 感知、建立隱藏 tkinter root、開啟 filedialog.askdirectory()
4. 以 subprocess 啟動 python.exe 執行腳本
5. 從暫存檔案讀取結果，正斜線轉回反斜線
6. 清理所有暫存檔案

### 3.3 解析路由 (`backend/routers/parse.py`)

```mermaid
graph TD
    A["POST /api/parse/folder"] --> B{"資料夾存在?"}
    B -->|否| ERR1["400 錯誤"]
    B -->|是| C{"已在解析中?"}
    C -->|是| ERR2["409 衝突"]
    C -->|否| D["啟動背景任務"]
    D --> E["in_progress = True"]
    E --> F["DailyReportParser 處理所有檔案"]
    F --> G["progress_callback 更新進度"]
    G --> H["儲存 records 至全域狀態"]
    H --> I["in_progress = False"]

    J["GET /api/parse/progress"] --> K["回傳進度狀態"]
    L["GET /api/parse/results"] --> M{"仍在解析?"}
    M -->|是| ERR3["409 衝突"]
    M -->|否| N["回傳結果"]
```

### 3.4 儀表板路由 (`backend/routers/dashboard.py`)

`convert_to_native(obj)` — 遞迴類型序列化：
- dict -> 遞迴處理 values
- list -> 遞迴處理 items
- np.integer -> int
- np.floating -> float
- np.ndarray -> .tolist()
- pd.Timestamp -> .isoformat()
- pd.isna -> None

### 3.5 績效路由 — 累計數據端點

`GET /api/performance/cumulative-data/{project_code}` 演算法：

```mermaid
graph TD
    A["篩選項目"] --> B["GroupBy Year SUM Qty cumsum"]
    B --> C{"start/end year 提供?"}
    C -->|否| D["使用數據範圍 end+3年"]
    C -->|是| E["使用提供的範圍"]
    D --> F{"target_qty 提供?"}
    E --> F
    F -->|否| G["估算為目前累計的 120%"]
    F -->|是| H["使用提供的值"]
    G --> I["current_pace = 最近 3 年平均"]
    H --> I
    I --> J["required_speed = remaining / remaining_years"]
    J --> K["projected_finish = last_year + remaining / pace"]
    K --> L["建立 chart_data 陣列"]
    L --> M["每年: plan, actual, recovery, projected"]
```

### 3.6 關鍵字路由 (`backend/routers/keyword.py`)

```mermaid
graph TD
    A["輸入: folder_path + keyword"] --> B["Glob PS-OHLR_DUAT_Daily Report_*.docx"]
    B --> C["排除 ~$ 暫存檔"]
    C --> D["遍歷每個檔案"]
    D --> E["python-docx 開啟"]
    E --> F["搜尋 paragraphs"]
    E --> G["搜尋 table cells"]
    F --> H["不區分大小寫子字串匹配"]
    G --> H
    H --> I["截斷文字至 500 字元"]
    I --> J["按文字內容去重"]
    J --> K["按檔案名稱分組結果"]
```

### 3.7 人力路由 (`backend/routers/manpower.py`)

`_serialize(obj)` 輔助函式：遞迴將 defaultdict 和巢狀結構轉換為純 dict/list 以供 JSON 序列化。

---

## 4. 數據流總覽

### 4.1 主要數據流：DOCX -> Dashboard -> 分析

```mermaid
graph TD
    DOCX["DOCX 檔案系統"] --> Parse["POST /api/parse/folder"]
    Parse -->|"背景任務 + 進度輪詢"| Parser["DailyReportParser.process_all"]
    Parser -->|"List of Dict records"| Dash["POST /api/dashboard/analyze"]
    Dash --> AGG["aggregate_records"]
    AGG --> CALC["calculate_summary"]
    CALC --> PIVOT["get_nth_pivot_by_week"]
    PIVOT --> Store["儲存至全域 analyzer"]

    Store --> DashAPI["Dashboard 端點<br/>stats/trends/distribution"]
    Store --> PerfAPI["POST /api/performance/set-data<br/>複製 df"]
    Store --> SCurveAPI["POST /api/scurve/set-data<br/>複製 df"]
    Store --> LagAPI["POST /api/lag/load-master<br/>載入 Master + summary"]
    Store --> ExportAPI["POST /api/export/dashboard<br/>讀取 analyzer 數據"]

    PerfAPI --> PerfCalc["PerformanceAnalyzer.analyze"]
    SCurveAPI --> SCurveCalc["calculate_scurve_data"]
    LagAPI --> LagCalc["LagAnalyzer.calculate"]
    ExportAPI --> ExcelFile["Excel 檔案下載"]
```

### 4.2 人力數據流（獨立）

```mermaid
graph TD
    DOCX["DOCX 檔案"] --> Scan["POST /api/manpower/scan"]
    Scan --> MP["ManpowerParser.process_all"]
    MP --> State["manpower_state records"]
    State --> Analysis["GET /api/manpower/analysis"]
    Analysis --> KPI["summary_kpis"]
    Analysis --> JT["job_type_manpower"]
    Analysis --> RF["role_frequency"]
    Analysis --> TD2["team_distribution"]
    Analysis --> WA["work_access_analysis"]
    State --> Export["POST /api/manpower/export"]
    Export --> Excel["Excel 4 sheets"]
```

### 4.3 關鍵字搜尋流程（獨立）

```mermaid
graph LR
    Input["folder_path + keyword"] --> Search["POST /api/keyword/search"]
    Search --> Glob["glob DOCX 檔案"]
    Glob --> Scan["python-docx 搜尋<br/>paragraphs + table cells"]
    Scan --> Results["filename + matches"]
```
