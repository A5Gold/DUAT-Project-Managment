# Product Requirements Document (PRD)

## MTR PS-OHLR DUAT - Daily Update Analysis Tool

**Version**: 3.0.0
**Last Updated**: 2026-02-13
**Status**: Reconstruction from Python Flet + FastAPI into Electron + React + FastAPI hybrid desktop application

---

## 1. Executive Summary

The MTR PS-OHLR DUAT (Daily Update Analysis Tool) is a desktop application used by the MTR Power System Overhead Line Renewal team to parse daily report DOCX files, aggregate project delivery data, and provide analytics dashboards for progress tracking. The reconstruction replaces the Python Flet UI with a React SPA running inside Electron, retains the FastAPI backend as a spawned sidecar process, and delivers a portable `.exe` desktop application.

---

## 2. Epic Summary

| Epic | Name                          | Priority | User Stories | Description                                         |
| ---- | ----------------------------- | -------- | ------------ | --------------------------------------------------- |
| E1   | Application Shell             | P0       | 1            | Electron shell managing Python backend lifecycle    |
| E2   | Data Ingestion - DOCX Parsing | P0       | 1            | Parse daily report DOCX files into structured data  |
| E3   | Manpower Data Ingestion       | P0       | 1            | Extract manpower deployment data from daily reports |
| E4   | Analytics Dashboard           | P0       | 2            | Aggregated statistics, trends, and distributions    |
| E5   | NTH Lag/Lead Analysis         | P0       | 2            | Planned vs actual progress comparison               |
| E6   | Performance Tracking          | P1       | 2            | Per-project weekly productivity and recovery paths  |
| E7   | S-Curve Generation            | P1       | 1            | Cumulative progress S-Curve charts and reports      |
| E8   | Keyword Search                | P1       | 1            | Full-text search across daily report DOCX files     |
| E9   | Manpower Analysis             | P1       | 1            | Workforce allocation and EPIC role statistics       |
| E10  | Internationalization          | P1       | 1            | English and Traditional Chinese language support    |
| E11  | Configuration Persistence     | P2       | 1            | Settings persistence between sessions               |
| E12  | Build and Distribution        | P2       | 1            | Portable .exe packaging                             |
| E13  | Documentation                 | P2       | 4            | Technical documentation deliverables                |

---

## 3. Epics and User Stories

### Epic 1: Application Shell (P0)

#### US-1.1: Desktop Application Lifecycle

**As a** user,
**I want to** launch the DUAT as a single desktop application that manages the Python backend automatically,
**so that** I do not need to start multiple processes manually.

**Acceptance Criteria**:

1. WHEN the user launches the application, THE Electron Shell SHALL spawn the FastAPI Sidecar as a child process on a localhost port
2. WHEN the FastAPI Sidecar is ready, THE Electron Shell SHALL load the React SPA in the main BrowserWindow
3. WHEN the user closes the application window, THE Electron Shell SHALL terminate the FastAPI Sidecar child process and release all resources
4. IF the FastAPI Sidecar fails to start within 15 seconds, THEN THE Electron Shell SHALL display an error dialog and allow the user to retry or exit
5. WHEN the user requests a file or folder selection, THE Electron Shell SHALL open a native OS file dialog via Electron IPC and return the selected path to the React SPA

---

### Epic 2: Data Ingestion - DOCX Parsing (P0)

#### US-2.1: Folder Parsing

**As a** user,
**I want to** select a folder of daily report DOCX files and have the system parse them into structured data,
**so that** I can generate dashboards and analysis.

**Acceptance Criteria**:

1. WHEN the user selects a folder path and triggers parsing, THE DOCX Parser SHALL scan for files matching `PS-OHLR_DUAT_Daily Report_*.docx` excluding temporary files prefixed with `~$`
2. WHEN processing a DOCX file, THE DOCX Parser SHALL extract date, project code (C####), quantity delivered, week number, and year from each matching record
3. WHEN processing a DOCX file, THE DOCX Parser SHALL identify blue-colored text in paragraphs and table cells to detect job type keywords (CBM, CM, PA work, HLM, Provide)
4. WHEN the DOCX Parser encounters a night shift row containing a blue-text keyword, THE DOCX Parser SHALL create a record with quantity zero for that keyword entry
5. WHEN processing a DOCX file, THE DOCX Parser SHALL extract the railway line code (KTL, TCL, AEL, TWL, ISL, TKL, EAL, SIL, TML, DRL) from each row text
6. IF a DOCX file cannot be opened, THEN THE DOCX Parser SHALL log the error and continue processing remaining files
7. WHEN parsing is complete, THE DOCX Parser SHALL return all extracted records with FullDate, Project, Qty Delivered, Week, Year, and Line fields
8. WHEN parsing is in progress, THE system SHALL provide progress updates (current file, percentage) via a polling endpoint

---

### Epic 3: Manpower Data Ingestion (P0)

#### US-3.1: Manpower Scan

**As a** user,
**I want to** extract manpower deployment data from daily reports,
**so that** I can analyse workforce allocation and EPIC role assignments.

**Acceptance Criteria**:

1. WHEN the user triggers a manpower scan, THE Manpower Parser SHALL parse the second table of each daily report DOCX to extract shift-level records
2. WHEN processing a shift cell, THE Manpower Parser SHALL split content into sections: HLM, C&R Works and Projects, Attendance, and Other Notable Items
3. WHEN extracting job data, THE Manpower Parser SHALL identify job type (CBM, CM, PA work, SPA work, HLM, C&R), project code, quantity, worker names, team counts, and EPIC role assignments (CP_P, CP_T, AP_E, SPC, HSM, NP)
4. WHEN extracting on-duty information, THE Manpower Parser SHALL parse worker names, team counts (S2-S5 format), apprentice names, and term labour counts
5. WHEN extracting leave data, THE Manpower Parser SHALL categorize leave entries into AL, SH, SL, RD, and Training types with associated names

---

### Epic 4: Analytics Dashboard (P0)

#### US-4.1: Dashboard Statistics

**As a** user,
**I want to** view aggregated project statistics, trends, and distributions on a dashboard,
**so that** I can monitor overall progress at a glance.

**Acceptance Criteria**:

1. WHEN dashboard analysis is triggered with parsed records, THE Dashboard Analyzer SHALL compute total records, total NTH, total quantity, unique project count, and last updated timestamp
2. WHEN computing trends, THE Dashboard Analyzer SHALL produce weekly delivery trends (Projects vs Jobs categories) and monthly delivery trends with configurable lookback periods
3. WHEN computing distributions, THE Dashboard Analyzer SHALL produce project distribution, keyword distribution, and railway line distribution breakdowns (NTH and Qty by line)
4. WHEN computing line distribution, THE Dashboard Analyzer SHALL produce line-by-project quantity breakdown and monthly line trend data
5. WHEN the user requests an NTH trend by project, THE Dashboard Analyzer SHALL produce a pivot of NTH values by week for each project

#### US-4.2: Dashboard Export

**As a** user,
**I want to** export dashboard data to Excel,
**so that** I can share and archive the analysis results.

**Acceptance Criteria**:

1. WHEN the user requests a dashboard export, THE system SHALL generate an Excel file with sheets: Raw Data, Summary by Project, NTH Trend by Week
2. WHEN the user requests to save to source folder, THE system SHALL save the Excel file as "Progress Dashboard + NTH.xlsx" in the original DOCX folder
3. THE exported Excel file SHALL preserve all data types and formatting

---

### Epic 5: NTH Lag/Lead Analysis (P0)

#### US-5.1: Project Master Import

**As a** user,
**I want to** import a Project Master Excel file,
**so that** I can compare planned progress against actual progress.

**Acceptance Criteria**:

1. WHEN the user uploads a Project Master Excel file, THE Lag Analyzer SHALL extract project number, title, start date, finish date, and target quantity for each project
2. THE Lag Analyzer SHALL perform case-insensitive column mapping to locate required fields
3. WHEN dashboard data is available, THE Lag Analyzer SHALL auto-match productivity (Qty per NTH) from the dashboard summary

#### US-5.2: Lag/Lead Calculation

**As a** user,
**I want to** calculate NTH lag/lead for all projects,
**so that** I can identify projects that are behind or ahead of schedule.

**Acceptance Criteria**:

1. WHEN the user triggers lag calculation, THE Lag Analyzer SHALL compute weeks elapsed, total weeks, target to date (linear interpolation), progress percentage, NTH lag/lead value, and status for each project
2. WHEN computing status, THE Lag Analyzer SHALL classify each project as URGENT (lag <= -10), BEHIND (lag <= -5), SLIGHT LAG (lag < 0), ON TRACK (lag < 5), or AHEAD (lag >= 5)
3. THE user SHALL be able to configure per-project: target quantity, productivity rate, and skip flag
4. WHEN the user requests a lag report export, THE Lag Analyzer SHALL generate an Excel file containing the full lag/lead analysis results

---

### Epic 6: Performance Tracking (P1)

#### US-6.1: Performance Metrics

**As a** user,
**I want to** view per-project performance metrics including weekly productivity,
**so that** I can assess whether projects will meet their targets.

**Acceptance Criteria**:

1. WHEN the user selects a project, THE Performance Analyzer SHALL compute weekly productivity (Qty/NTH), success rate, weeks met/missed target, and current pace (last 12 weeks average)
2. THE Performance Analyzer SHALL provide a list of available projects (codes starting with C)
3. THE system SHALL generate a weekly performance bar chart (green=met, red=missed) with target line

#### US-6.2: Recovery Path and Cumulative Progress

**As a** user,
**I want to** see cumulative progress and recovery projections,
**so that** I can plan corrective actions.

**Acceptance Criteria**:

1. WHEN the user requests recovery analysis, THE system SHALL compute required weekly rate, weeks to complete at current pace, and on-track status
2. THE system SHALL generate a cumulative progress chart with plan (linear), actual, recovery path, and projected pace lines
3. THE system SHALL calculate projected finish date based on current pace

---

### Epic 7: S-Curve Generation (P1)

#### US-7.1: S-Curve Charts and Reports

**As a** user,
**I want to** generate S-Curve charts for specific projects,
**so that** I can visualize cumulative progress against planned targets.

**Acceptance Criteria**:

1. WHEN the user provides a project code, target quantity, and start/end period, THE S-Curve Generator SHALL compute cumulative planned (linear) and actual progress data points
2. THE system SHALL generate an S-Curve chart with target (blue dashed), actual (green solid), and fill between (green if ahead, red if behind)
3. THE system SHALL generate an Excel report with Week/Target/Actual/Variance data and embedded chart
4. IF the project code has no matching data, THEN THE system SHALL return a descriptive error message

---

### Epic 8: Keyword Search (P1)

#### US-8.1: DOCX Keyword Search

**As a** user,
**I want to** search all daily report DOCX files for specific keywords,
**so that** I can find relevant entries across the entire report archive.

**Acceptance Criteria**:

1. WHEN the user provides a folder path and keyword, THE system SHALL scan all matching DOCX files
2. THE system SHALL perform case-insensitive keyword matching in paragraphs and table cells
3. THE system SHALL return file name, location (paragraph or table cell reference), and surrounding context (up to 500 chars) for each match
4. THE system SHALL deduplicate matches by text content within each file
5. WHEN no matches are found, THE system SHALL display a message indicating zero results

---

### Epic 9: Manpower Analysis (P1)

#### US-9.1: Manpower Statistics

**As a** user,
**I want to** view manpower deployment statistics,
**so that** I can optimize workforce allocation.

**Acceptance Criteria**:

1. WHEN manpower scan results are available, THE Manpower Analyzer SHALL compute KPIs: total work entries, average workers per job, unique staff count, and top role holder
2. THE Manpower Analyzer SHALL produce average team size by job type and average EPIC roles per job type
3. THE Manpower Analyzer SHALL produce a per-person frequency table of EPIC role assignments (sorted by total descending)
4. THE Manpower Analyzer SHALL categorize jobs into work access types: Possession (CP(P) present), PA work, SPA work, and Other, with average safety role counts per category
5. THE Manpower Analyzer SHALL compute weekly team distribution (S2/S3/S4/S5 per week)
6. WHEN the user requests export, THE system SHALL generate an Excel file with 4 sheets: Raw Data, Job Type Summary, Role Frequency, Weekly Team Distribution

---

### Epic 10: Internationalization (P1)

#### US-10.1: Language Switching

**As a** user,
**I want to** switch between English and Traditional Chinese at any time,
**so that** I can use the application in my preferred language.

**Acceptance Criteria**:

1. THE React SPA SHALL support two languages: English (en) and Traditional Chinese (zh)
2. WHEN the user toggles the language, THE Zustand Store SHALL update the language preference and re-render all visible text labels
3. WHEN the application restarts, THE system SHALL restore the previously selected language
4. THE system SHALL use a translation function that accepts a key and optional interpolation parameters

---

### Epic 11: Configuration Persistence (P2)

#### US-11.1: Settings Persistence

**As a** user,
**I want to** have my settings persist between sessions,
**so that** I do not need to reconfigure the application each time.

**Acceptance Criteria**:

1. THE FastAPI Sidecar SHALL load configuration from a JSON file on startup, merging saved values with defaults
2. WHEN the user changes a setting, THE system SHALL save the updated configuration immediately
3. THE Zustand Store SHALL persist language and last folder path to browser local storage
4. IF the configuration file does not exist or is corrupted, THEN THE system SHALL use default values and log a warning
5. Configuration fields: last_folder, language, dark_mode, default_productivity, keywords

---

### Epic 12: Build and Distribution (P2)

#### US-12.1: Portable Desktop Build

**As a** developer,
**I want to** package the application as a single portable `.exe` file,
**so that** end users can run it without installing Python, Node.js, or any dependencies.

**Acceptance Criteria**:

1. THE build process SHALL use electron-builder to package the Electron app with the bundled React SPA
2. THE build process SHALL use PyInstaller to bundle the FastAPI Sidecar and all Python dependencies
3. THE build process SHALL include the bundled Python backend within the Electron application resources
4. WHEN the packaged application is launched on a Windows machine without Python or Node.js, THE application SHALL start and function correctly

---

### Epic 13: Documentation (P2)

#### US-13.1: Field Mapping Specification

**As a** developer,
**I want to** have a field mapping specification document,
**so that** I have a canonical reference for all data field names.

**Acceptance Criteria**:

1. THE document SHALL define canonical field names for all data structures
2. THE document SHALL provide mapping from legacy to canonical field names
3. THE document SHALL specify data type, description, and source module for each field

#### US-13.2: Algorithm Logic Document

**As a** developer,
**I want to** have algorithm documentation for all functions,
**so that** I can understand the computation logic without reading source code.

**Acceptance Criteria**:

1. THE document SHALL describe the algorithm for every public function in the analysis module
2. THE document SHALL include input/output specifications and mathematical formulas

#### US-13.3: Architecture Document

**As a** developer,
**I want to** have an architecture document,
**so that** I can understand the system layers and communication patterns.

**Acceptance Criteria**:

1. THE document SHALL describe the four-layer architecture
2. THE document SHALL include system architecture diagrams
3. THE document SHALL describe IPC and HTTP REST communication patterns

#### US-13.4: Product Requirements Document

**As a** product owner,
**I want to** have a PRD with epics and user stories,
**so that** I have a structured backlog for the reconstruction project.

**Acceptance Criteria**:

1. THE document SHALL organize requirements into prioritized epics
2. THE document SHALL include user stories with acceptance criteria

---

## 4. Non-Functional Requirements

### 4.1 Performance

- DOCX parsing SHALL process at least 10 files per second on a standard desktop machine
- Dashboard analysis SHALL complete within 2 seconds for up to 10,000 records
- API responses SHALL return within 500ms for non-export endpoints

### 4.2 Reliability

- THE application SHALL handle corrupted DOCX files gracefully (log and skip)
- THE application SHALL handle missing Project Master columns gracefully (fallback mapping)
- THE application SHALL not crash on empty datasets (return empty results)

### 4.3 Usability

- THE application SHALL provide progress feedback during long-running operations (parsing)
- THE application SHALL support English and Traditional Chinese
- THE application SHALL persist user preferences between sessions

### 4.4 Portability

- THE packaged application SHALL run on Windows 10/11 without additional dependencies
- THE application SHALL bind to localhost only (no network exposure)

---

## 5. Data Flow Summary

```
DOCX Files --> [Parse] --> Records --> [Dashboard] --> Stats/Trends/Distributions
                                          |
                                          +--> [Lag Analysis] --> Lag/Lead Results
                                          +--> [Performance] --> Productivity Metrics
                                          +--> [S-Curve] --> Cumulative Progress
                                          +--> [Export] --> Excel Files

DOCX Files --> [Manpower Parse] --> Shift Records --> [Manpower Analysis] --> KPIs/Reports

DOCX Files --> [Keyword Search] --> Search Results
```

---

## 6. Glossary

| Term           | Definition                                                      |
| -------------- | --------------------------------------------------------------- |
| DUAT           | Daily Update Analysis Tool                                      |
| NTH            | Number of Times on Hand - cumulative delivery count per project |
| EPIC           | Safety role assignment system for railway maintenance           |
| CP(P)          | Competent Person (Possession)                                   |
| CP(T)          | Competent Person (Track)                                        |
| AP(E)          | Authorized Person (Electrical)                                  |
| SPC            | Second Person Checker                                           |
| HSM            | Hand Signal Man                                                 |
| NP             | Nominated Person                                                |
| S-Curve        | Cumulative progress chart showing planned vs actual             |
| Lag/Lead       | Difference between planned and actual progress in NTH units     |
| Project Master | Excel file with project targets and schedules                   |
| Possession     | Engineering train access in electrically isolated zone          |
| PA work        | Pedestrian Access work                                          |
| SPA work       | Special Pedestrian Access work                                  |
