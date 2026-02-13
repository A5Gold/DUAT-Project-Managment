# MTR PS-OHLR DUAT - Analysis Module
"""
Analysis modules for dashboard, lag analysis, S-curve, and performance tracking.
"""

from .dashboard import (
    aggregate_records,
    calculate_summary,
    get_weekly_trend,
    get_monthly_trend,
    get_project_distribution,
    get_keyword_distribution,
    get_nth_pivot_by_week,
    export_dashboard_excel,
    DashboardAnalyzer
)

from .lag_analysis import (
    get_status,
    load_project_master,
    calculate_nth_lag_lead,
    export_lag_report,
    LagAnalyzer
)

from .scurve import (
    calculate_scurve_data,
    plot_scurve,
    generate_scurve_excel,
    SCurveGenerator
)

from .performance import (
    calculate_performance_metrics,
    get_recovery_path,
    plot_performance_chart,
    plot_cumulative_progress,
    PerformanceAnalyzer
)

from .manpower import (
    get_daily_headcount,
    get_team_distribution,
    get_job_type_manpower,
    get_role_frequency,
    get_work_access_analysis,
    get_individual_stats,
    get_summary_kpis,
    export_manpower_excel,
    ManpowerAnalyzer
)

__all__ = [
    # Dashboard
    'aggregate_records',
    'calculate_summary',
    'get_weekly_trend',
    'get_monthly_trend',
    'get_project_distribution',
    'get_keyword_distribution',
    'get_nth_pivot_by_week',
    'export_dashboard_excel',
    'DashboardAnalyzer',
    # Lag Analysis
    'get_status',
    'load_project_master',
    'calculate_nth_lag_lead',
    'export_lag_report',
    'LagAnalyzer',
    # S-Curve
    'calculate_scurve_data',
    'plot_scurve',
    'generate_scurve_excel',
    'SCurveGenerator',
    # Performance
    'calculate_performance_metrics',
    'get_recovery_path',
    'plot_performance_chart',
    'plot_cumulative_progress',
    'PerformanceAnalyzer',
    # Manpower
    'get_daily_headcount',
    'get_team_distribution',
    'get_job_type_manpower',
    'get_role_frequency',
    'get_possession_vs_track_access',
    'get_individual_stats',
    'get_summary_kpis',
    'export_manpower_excel',
    'ManpowerAnalyzer',
]
