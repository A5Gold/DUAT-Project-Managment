type Locale = 'en' | 'zh'
type Translations = Record<string, Record<string, string>>

const translations: Record<Locale, Translations> = {
  en: {
    app: {
      title: 'DUAT Project Management',
      version: 'Version',
      loading: 'Loading application...',
    },
    nav: {
      home: 'Home',
      generate: 'Generate',
      dashboard: 'Dashboard',
      lagAnalysis: 'Lag Analysis',
      performance: 'Performance',
      keywordSearch: 'Keyword Search',
      manpower: 'Manpower',
    },
    home: {
      title: 'Home',
      selectFolder: 'Select Folder',
      folderPath: 'Folder Path',
      startParse: 'Start Parsing',
      parsing: 'Parsing...',
      parseComplete: 'Parsing Complete',
      noFolder: 'No folder selected',
    },
    generate: {
      title: 'Generate Report',
      analyzeRecords: 'Analyze Records',
      loadExcel: 'Load Excel',
      analyzing: 'Analyzing...',
      complete: 'Analysis Complete',
    },
    dashboard: {
      title: 'Dashboard',
      totalRecords: 'Total Records',
      totalNTH: 'Total NTH',
      totalQty: 'Total Quantity',
      uniqueProjects: 'Unique Projects',
      lastUpdated: 'Last Updated',
      weeklyTrend: 'Weekly Trend',
      monthlyTrend: 'Monthly Trend',
      projectDist: 'Project Distribution',
      keywordDist: 'Keyword Distribution',
      lineDist: 'Line Distribution',
      rawData: 'Raw Data',
      pivot: 'Pivot Table',
      nthByProject: 'NTH by Project',
      exportExcel: 'Export to Excel',
      noData: 'No Dashboard Data',
      noDataHint: 'Please go to Home to parse DOCX files, then use Generate to analyze data.',
    },
    lag: {
      title: 'Lag Analysis',
      loadMaster: 'Load Master',
      calculate: 'Calculate',
      results: 'Results',
      statusLegend: 'Status Legend',
      projectNo: 'Project No.',
      targetQty: 'Target Quantity',
      actualQty: 'Actual Quantity',
      progress: 'Progress',
      status: 'Status',
      nthLagLead: 'NTH Lag/Lead',
      uploadMaster: 'Upload Master File',
      noResults: 'No results available',
    },
    performance: {
      title: 'Performance Analysis',
      selectProject: 'Select Project',
      analyze: 'Analyze',
      weeklyChart: 'Weekly Chart',
      cumulativeChart: 'Cumulative Chart',
      successRate: 'Success Rate',
      currentPace: 'Current Pace',
      recovery: 'Recovery',
      weeksToComplete: 'Weeks to Complete',
      onTrack: 'On Track',
      offTrack: 'Off Track',
    },
    scurve: {
      title: 'S-Curve',
      calculate: 'Calculate',
      targetQty: 'Target Quantity',
      startPeriod: 'Start Period',
      endPeriod: 'End Period',
      chart: 'Chart',
      exportExcel: 'Export to Excel',
    },
    keyword: {
      title: 'Keyword Search',
      searchPlaceholder: 'Enter keyword to search...',
      search: 'Search',
      noResults: 'No results found',
      results: 'Results',
      fileName: 'File Name',
      location: 'Location',
      context: 'Context',
    },
    manpower: {
      title: 'Manpower Analysis',
      scan: 'Scan',
      analysis: 'Analysis',
      export: 'Export',
      totalJobs: 'Total Jobs',
      avgWorkers: 'Average Workers',
      uniqueStaff: 'Unique Staff',
      topRole: 'Top Role',
      kpis: 'KPIs',
      roleFrequency: 'Role Frequency',
      teamDistribution: 'Team Distribution',
    },
    common: {
      save: 'Save',
      cancel: 'Cancel',
      reset: 'Reset',
      export: 'Export',
      upload: 'Upload',
      download: 'Download',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      confirm: 'Confirm',
      back: 'Back',
      next: 'Next',
      page: 'Page',
      of: 'of',
      noData: 'No data available',
      retry: 'Retry',
    },
    parse: {
      progress: 'Processing {current} of {total}',
    },
  },
  zh: {
    app: {
      title: 'DUAT 專案管理系統',
      version: '版本',
      loading: '應用程式載入中...',
    },
    nav: {
      home: '首頁',
      generate: '產生報表',
      dashboard: '儀表板',
      lagAnalysis: '落後分析',
      performance: '績效分析',
      keywordSearch: '關鍵字搜尋',
      manpower: '人力資源',
    },
    home: {
      title: '首頁',
      selectFolder: '選擇資料夾',
      folderPath: '資料夾路徑',
      startParse: '開始解析',
      parsing: '解析中...',
      parseComplete: '解析完成',
      noFolder: '尚未選擇資料夾',
    },
    generate: {
      title: '產生報表',
      analyzeRecords: '分析紀錄',
      loadExcel: '載入 Excel',
      analyzing: '分析中...',
      complete: '分析完成',
    },
    dashboard: {
      title: '儀表板',
      totalRecords: '總紀錄數',
      totalNTH: '總 NTH 數',
      totalQty: '總數量',
      uniqueProjects: '專案數',
      lastUpdated: '最後更新',
      weeklyTrend: '每週趨勢',
      monthlyTrend: '每月趨勢',
      projectDist: '專案分佈',
      keywordDist: '關鍵字分佈',
      lineDist: '路線分佈',
      rawData: '原始資料',
      pivot: '樞紐分析表',
      nthByProject: '各專案 NTH',
      exportExcel: '匯出至 Excel',
      noData: '尚無儀表板資料',
      noDataHint: '請先至首頁解析 DOCX 檔案，再使用「產生報表」進行分析。',
    },
    lag: {
      title: '落後分析',
      loadMaster: '載入主檔',
      calculate: '計算',
      results: '結果',
      statusLegend: '狀態圖例',
      projectNo: '專案編號',
      targetQty: '目標數量',
      actualQty: '實際數量',
      progress: '進度',
      status: '狀態',
      nthLagLead: 'NTH 落後/超前',
      uploadMaster: '上傳主檔',
      noResults: '暫無結果',
    },
    performance: {
      title: '績效分析',
      selectProject: '選擇專案',
      analyze: '分析',
      weeklyChart: '每週圖表',
      cumulativeChart: '累計圖表',
      successRate: '達成率',
      currentPace: '目前進度',
      recovery: '恢復',
      weeksToComplete: '預計完成週數',
      onTrack: '進度正常',
      offTrack: '進度落後',
    },
    scurve: {
      title: 'S 曲線',
      calculate: '計算',
      targetQty: '目標數量',
      startPeriod: '起始期間',
      endPeriod: '結束期間',
      chart: '圖表',
      exportExcel: '匯出至 Excel',
    },
    keyword: {
      title: '關鍵字搜尋',
      searchPlaceholder: '輸入關鍵字搜尋...',
      search: '搜尋',
      noResults: '查無結果',
      results: '搜尋結果',
      fileName: '檔案名稱',
      location: '位置',
      context: '上下文',
    },
    manpower: {
      title: '人力資源分析',
      scan: '掃描',
      analysis: '分析',
      export: '匯出',
      totalJobs: '總工作數',
      avgWorkers: '平均工人數',
      uniqueStaff: '不重複人員',
      topRole: '最多角色',
      kpis: '關鍵績效指標',
      roleFrequency: '角色頻率',
      teamDistribution: '團隊分佈',
    },
    common: {
      save: '儲存',
      cancel: '取消',
      reset: '重設',
      export: '匯出',
      upload: '上傳',
      download: '下載',
      loading: '載入中...',
      error: '錯誤',
      success: '成功',
      confirm: '確認',
      back: '返回',
      next: '下一步',
      page: '頁',
      of: '之',
      noData: '暫無資料',
      retry: '重試',
    },
    parse: {
      progress: '正在處理第 {current} 筆，共 {total} 筆',
    },
  },
}

let currentLocale: Locale = 'en'

function setLocale(locale: Locale): void {
  currentLocale = locale
}

function getLocale(): Locale {
  return currentLocale
}

function t(key: string, params?: Record<string, string | number>): string {
  const parts = key.split('.')
  if (parts.length !== 2) {
    return key
  }

  const [group, subkey] = parts
  const groupTranslations = translations[currentLocale][group]

  if (!groupTranslations || !(subkey in groupTranslations)) {
    return key
  }

  let result = groupTranslations[subkey]

  if (params) {
    for (const [paramName, paramValue] of Object.entries(params)) {
      result = result.replace(`{${paramName}}`, String(paramValue))
    }
  }

  return result
}

export { currentLocale, setLocale, getLocale, t }
export type { Locale, Translations }
