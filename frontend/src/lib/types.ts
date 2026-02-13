// =============================================================================
// DUAT Project Management - TypeScript Type Definitions
// =============================================================================

// -----------------------------------------------------------------------------
// Generic API Envelope
// -----------------------------------------------------------------------------

export type ApiResponse<T> = {
  success: boolean;
  data?: T;
  error?: string;
  meta?: {
    total: number;
    page: number;
    limit: number;
  };
};

// -----------------------------------------------------------------------------
// DOCX Parser Output
// -----------------------------------------------------------------------------

export type ParsedRecord = {
  FullDate: string;
  Project: string;
  'Qty Delivered': number;
  Week: string;
  Year: string;
  Line: string;
};

// -----------------------------------------------------------------------------
// Dashboard Derived Fields
// -----------------------------------------------------------------------------

export type DerivedRecord = ParsedRecord & {
  Day: string;
  Date: string;
  DateObj: string;
  Month: string;
  YearWeek: string;
  Category: 'Jobs' | 'Projects';
};

// -----------------------------------------------------------------------------
// Dashboard Statistics
// -----------------------------------------------------------------------------

export type DashboardStats = {
  total_records: number;
  total_nth: number;
  total_qty: number;
  unique_projects: number;
  last_updated: string;
};

// -----------------------------------------------------------------------------
// Project Summary
// -----------------------------------------------------------------------------

export type ProjectSummary = {
  Rank: number;
  Project: string;
  'Qty Delivered': number;
  'Total NTH': number;
  'Qty per NTH': number;
  'Avg Qty per Week': number;
  'Avg Qty per Month': number;
  'Avg NTH per Week': number;
  'Avg NTH per Month': number;
};

// -----------------------------------------------------------------------------
// Trend Data
// -----------------------------------------------------------------------------

export type WeeklyTrend = {
  week: string;
  Projects: number;
  Jobs: number;
};

export type MonthlyTrend = {
  month: string;
  count: number;
};

// -----------------------------------------------------------------------------
// Distribution
// -----------------------------------------------------------------------------

export type Distribution = {
  name: string;
  value: number;
};

export type LineDistribution = {
  line: string;
  nth: number;
  qty: number;
};

// -----------------------------------------------------------------------------
// Lag / Project Master
// -----------------------------------------------------------------------------

export type LagProject = {
  Project: string;
  Title: string;
  'Start Date': string;
  'End Date': string;
  'Target Qty': number;
  'Actual Qty': number;
  'Target % (Linear)': number;
  'Progress %': number;
  Productivity: number;
  'NTH Lag/Lead': number;
  Status: string;
  'Status Color': string;
};

export type LagProjectConfig = {
  target_qty: number;
  productivity: number;
  source: 'default' | 'daily_report' | 'user_input';
  skip: boolean;
};

export type StatusLegend = {
  status: string;
  color: string;
  threshold: string;
};

// -----------------------------------------------------------------------------
// Performance & Recovery
// -----------------------------------------------------------------------------

export type PerformanceMetrics = {
  total_weeks: number;
  weeks_met_target: number;
  weeks_missed: number;
  success_rate: number;
  target_productivity: number;
  current_pace: number;
  avg_productivity: number;
};

export type WeeklyPerformance = {
  Year: number;
  Week: number;
  'Qty Delivered': number;
  NTH_Count: number;
  'Actual Productivity': number;
  Label: string;
};

export type RecoveryPath = {
  required_weekly: number;
  required_productivity: number;
  on_track: boolean;
  weeks_to_complete: number | null;
};

// -----------------------------------------------------------------------------
// S-Curve
// -----------------------------------------------------------------------------

export type CumulativeDataPoint = {
  year: number;
  plan: number;
  actual: number | null;
  recovery: number | null;
  projected: number | null;
};

export type CumulativeMetrics = {
  current_pace: number;
  required_speed: number;
  projected_finish: string | null;
  total_actual: number;
  target_qty: number;
  on_track: boolean;
};

export type SCurveRequest = {
  project_code: string;
  target_qty: number;
  start_year: number;
  start_week: number;
  end_year: number;
  end_week: number;
};

export type SCurveResult = {
  week_labels: string[];
  cumulative_target: number[];
  cumulative_actual: number[];
  progress_pct: number;
};

// -----------------------------------------------------------------------------
// Manpower
// -----------------------------------------------------------------------------

export type Job = {
  type: string;
  project_code: string | null;
  description: string;
  qty: number;
  done_by_raw: string;
  team_counts: Record<string, number>;
  worker_names: string[];
  total_workers: number;
  roles: {
    EPIC: string;
    CP_P: string[];
    CP_T: string[];
    AP_E: string[];
    SPC: string[];
    HSM: string[];
    NP: string[];
  };
};

export type ShiftRecord = {
  date: string;
  day_of_week: string;
  shift: 'Day' | 'Night';
  week: string;
  year: string;
  jobs: Job[];
  on_duty_names: string[];
  on_duty_team_counts: Record<string, number>;
  apprentices: string[];
  term_labour_count: number;
  leave: {
    AL: string[];
    SH: string[];
    SL: string[];
    RD: string[];
    Training: string[];
  };
};

export type ManpowerKPIs = {
  total_jobs: number;
  avg_workers_per_job: number;
  unique_staff: number;
  top_role_holder: string;
};

// -----------------------------------------------------------------------------
// App Configuration
// -----------------------------------------------------------------------------

export type AppConfig = {
  last_folder: string;
  language: 'en' | 'zh';
  dark_mode: boolean;
  default_productivity: number;
  keywords: string[];
};

// -----------------------------------------------------------------------------
// Parse Progress & Search
// -----------------------------------------------------------------------------

export type ParseProgress = {
  status: 'idle' | 'parsing' | 'complete' | 'error';
  current_file: string;
  progress: number;
  total_files: number;
  processed_files: number;
  error?: string;
};

export type KeywordSearchResult = {
  file_name: string;
  location: string;
  context: string;
};

// -----------------------------------------------------------------------------
// UI / Notifications
// -----------------------------------------------------------------------------

export type Notification = {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
};
