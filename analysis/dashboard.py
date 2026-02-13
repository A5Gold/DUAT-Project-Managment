# MTR PS-OHLR DUAT - Dashboard Analysis
"""
Dashboard data aggregation and summary calculations.
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def aggregate_records(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Aggregate raw records into a DataFrame with proper formatting.
    
    Args:
        records: List of record dictionaries from DOCX parsing
        
    Returns:
        Cleaned and formatted DataFrame
    """
    if not records:
        return pd.DataFrame()
    
    df = pd.DataFrame(records)
    
    # Extract day and date components
    df["Day"] = df["FullDate"].str.extract(r'^([A-Za-z]{3})', expand=False)
    df["Date"] = df["FullDate"].str.replace(r'^[A-Za-z]{3}\s+', '', regex=True).str.strip()
    df["Week"] = df["Week"].astype(str).str.extract(r'(\d+)')[0]
    
    # Parse date objects
    df["DateObj"] = pd.to_datetime(
        df["Date"] + '/' + df["Year"],
        format='%d/%m/%Y', 
        errors='coerce'
    )
    df["Month"] = df["DateObj"].dt.strftime('%Y-%m')
    
    return df


def calculate_summary(df: pd.DataFrame, current_week: int = None, current_month: int = None) -> pd.DataFrame:
    """
    Calculate summary statistics by project.
    
    Args:
        df: DataFrame with raw data
        current_week: Current week number (default: max from data)
        current_month: Current month (default: current datetime month)
        
    Returns:
        Summary DataFrame with statistics per project
    """
    if df.empty:
        return pd.DataFrame()
    
    if current_week is None:
        current_week = df['Week'].astype(float).max() if 'Week' in df.columns else 44
    if current_month is None:
        current_month = datetime.now().month
    
    # Clean data
    df_clean = df.dropna(subset=["DateObj", "Month", "Week"]).copy()
    raw_df = df[["Year", "Day", "Date", "Week", "Project", "Qty Delivered"]].copy()
    
    # Calculate NTH totals
    nth_total = raw_df.groupby("Project").size().reset_index(name="Total NTH")
    
    # Calculate quantity totals
    summary_qty = df_clean.groupby("Project", as_index=False)["Qty Delivered"].sum()
    
    # Merge and calculate derived metrics
    summary = summary_qty.merge(nth_total, on="Project", how="left").fillna(0)
    summary["Total NTH"] = summary["Total NTH"].astype(int)
    summary["Qty per NTH"] = (summary["Qty Delivered"] / summary["Total NTH"].replace(0, 1)).round(2)
    summary["Avg Qty per Week"] = (summary["Qty Delivered"] / current_week).round(2)
    summary["Avg Qty per Month"] = (summary["Qty Delivered"] / current_month).round(2)
    summary["Avg NTH per Week"] = (summary["Total NTH"] / current_week).round(2)
    summary["Avg NTH per Month"] = (summary["Total NTH"] / current_month).round(2)
    
    # Sort and rank
    summary = summary.sort_values("Qty Delivered", ascending=False)
    summary.insert(0, "Rank", range(1, len(summary) + 1))
    
    return summary


def get_weekly_trend(df: pd.DataFrame, weeks: int = 12) -> Tuple[List[str], Dict[str, List[int]]]:
    """
    Get weekly trend data for Projects vs Jobs.
    
    Args:
        df: DataFrame with raw data
        weeks: Number of recent weeks to include
        
    Returns:
        Tuple of (week labels, category data dict)
    """
    if df is None or df.empty:
        return [], {}
    
    try:
        df_copy = df.copy()
        
        # Job keywords
        job_keywords = ['CBM', 'CM', 'PA work', 'HLM', 'Provide']
        
        # Create YearWeek column
        if 'Year' in df_copy.columns and 'Week' in df_copy.columns:
            df_copy['Year'] = pd.to_numeric(df_copy['Year'], errors='coerce')
            df_copy['Week'] = pd.to_numeric(df_copy['Week'], errors='coerce')
            df_copy = df_copy.dropna(subset=['Year', 'Week'])
            df_copy['YearWeek'] = (
                df_copy['Year'].astype(int).astype(str) + '-W' + 
                df_copy['Week'].astype(int).astype(str).str.zfill(2)
            )
        elif 'Date' in df_copy.columns:
            df_copy['DateObj'] = pd.to_datetime(df_copy['Date'], errors='coerce', dayfirst=True)
            df_copy = df_copy.dropna(subset=['DateObj'])
            df_copy['Week'] = df_copy['DateObj'].dt.isocalendar().week
            df_copy['Year'] = df_copy['DateObj'].dt.year
            df_copy['YearWeek'] = (
                df_copy['Year'].astype(str) + '-W' + 
                df_copy['Week'].astype(str).str.zfill(2)
            )
        else:
            return [], {}
        
        # Classify each row
        def classify_row(project_name):
            project_str = str(project_name).upper()
            for kw in job_keywords:
                if kw.upper() in project_str:
                    return 'Jobs'
            return 'Projects'
        
        df_copy['Category'] = df_copy['Project'].apply(classify_row)
        
        # Get unique weeks sorted (last N weeks)
        week_list = sorted(df_copy['YearWeek'].unique())[-weeks:]
        
        # Count NTH per week per category
        weekly_data = {}
        for cat in ['Projects', 'Jobs']:
            cat_data = df_copy[df_copy['Category'] == cat]
            weekly_counts = cat_data.groupby('YearWeek').size()
            weekly_data[cat] = [weekly_counts.get(w, 0) for w in week_list]
        
        return week_list, weekly_data
        
    except Exception as e:
        logger.error(f"Error in weekly trend: {e}")
        return [], {}


def get_monthly_trend(df: pd.DataFrame, months: int = 6) -> Tuple[List[str], List[int]]:
    """
    Get NTH trend data grouped by month.
    
    Args:
        df: DataFrame with raw data
        months: Number of recent months to include
        
    Returns:
        Tuple of (month labels, NTH counts)
    """
    if df is None or df.empty:
        return [], []
    
    try:
        df_copy = df.copy()
        
        if 'Year' in df_copy.columns and 'Week' in df_copy.columns:
            df_copy['Year'] = pd.to_numeric(df_copy['Year'], errors='coerce')
            df_copy['Week'] = pd.to_numeric(df_copy['Week'], errors='coerce')
            df_copy = df_copy.dropna(subset=['Year', 'Week'])
            df_copy['Month'] = ((df_copy['Week'] - 1) // 4.33 + 1).astype(int).clip(1, 12)
            df_copy['YearMonth'] = (
                df_copy['Year'].astype(int).astype(str) + '-' + 
                df_copy['Month'].astype(str).str.zfill(2)
            )
            monthly = df_copy.groupby('YearMonth').size().reset_index(name='NTH')
            monthly = monthly.sort_values('YearMonth').tail(months)
            return monthly['YearMonth'].tolist(), monthly['NTH'].tolist()
        elif 'Date' in df_copy.columns:
            df_copy['DateObj'] = pd.to_datetime(df_copy['Date'], errors='coerce', dayfirst=True)
            df_copy = df_copy.dropna(subset=['DateObj'])
            df_copy['YearMonth'] = df_copy['DateObj'].dt.strftime('%Y-%m')
            monthly = df_copy.groupby('YearMonth').size().reset_index(name='NTH')
            monthly = monthly.sort_values('YearMonth').tail(months)
            return monthly['YearMonth'].tolist(), monthly['NTH'].tolist()
            
    except Exception as e:
        logger.error(f"Error in monthly trend: {e}")
    
    return [], []


def get_project_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """
    Get NTH distribution by project.
    
    Args:
        df: DataFrame with raw data
        
    Returns:
        Dictionary of project -> NTH count
    """
    if df is None or df.empty:
        return {}
    
    try:
        if 'Project' in df.columns:
            project_nth = df.groupby('Project').size()
            # Rename "Provide" to full name
            project_nth = project_nth.rename(
                index={'Provide': 'Provide manpower for switching'}
            )
            return project_nth.to_dict()
    except Exception as e:
        logger.error(f"Error in project distribution: {e}")
    
    return {}


def get_keyword_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """
    Get NTH distribution by keyword jobs.
    
    Args:
        df: DataFrame with raw data
        
    Returns:
        Dictionary of keyword -> NTH count
    """
    if df is None or df.empty:
        return {}
    
    try:
        keywords = ['CBM', 'CM', 'PA work', 'HLM', 'Provide']
        keyword_totals = {}
        
        if 'Project' in df.columns:
            for kw in keywords:
                mask = df['Project'].astype(str).str.upper().str.contains(
                    kw.upper(), na=False
                )
                total = mask.sum()
                if total > 0:
                    display_name = 'Provide manpower for switching' if kw == 'Provide' else kw
                    keyword_totals[display_name] = total
        
        return keyword_totals
    except Exception as e:
        logger.error(f"Error in keyword distribution: {e}")
    
    return {}


def get_nth_pivot_by_week(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create NTH pivot table by week and project.
    
    Args:
        df: Cleaned DataFrame with YearWeek column
        
    Returns:
        Pivot table DataFrame
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    try:
        df_copy = df.copy()
        
        # Ensure YearWeek column exists
        if 'YearWeek' not in df_copy.columns:
            df_copy['YearWeek'] = (
                df_copy['Year'].astype(str) + '-W' + 
                df_copy['Week'].astype(str).str.zfill(2)
            )
        
        # Count NTH per project per week
        nth_by_week = df_copy.groupby(['YearWeek', 'Project']).size().reset_index(name='NTH_Count')
        nth_pivot = nth_by_week.pivot(
            index='YearWeek', 
            columns='Project', 
            values='NTH_Count'
        ).fillna(0)
        
        # Sort by week chronologically
        nth_pivot = nth_pivot.sort_index()
        
        return nth_pivot
    except Exception as e:
        logger.error(f"Error creating NTH pivot: {e}")
        return pd.DataFrame()


def export_dashboard_excel(
    raw_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    nth_pivot: pd.DataFrame,
    output_path: Path
) -> bool:
    """
    Export dashboard data to Excel file.
    
    Args:
        raw_df: Raw data DataFrame
        summary_df: Summary by project DataFrame
        nth_pivot: NTH trend pivot table
        output_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            raw_df.to_excel(writer, sheet_name='Raw Data', index=False)
            summary_df.to_excel(writer, sheet_name='Summary by Project', index=False)
            if not nth_pivot.empty:
                nth_pivot.to_excel(writer, sheet_name='NTH Trend by Week', index=True)
        return True
    except Exception as e:
        logger.error(f"Error exporting Excel: {e}")
        return False


class DashboardAnalyzer:
    """High-level dashboard data manager."""
    
    def __init__(self):
        self.df = None
        self.summary = None
        self.last_updated = None
        self.nth_trend = None
    
    def load_from_records(self, records: List[Dict[str, Any]], max_week: int = None):
        """Load dashboard data from parsed records."""
        if not records:
            return False
        
        self.df = aggregate_records(records)
        if self.df.empty:
            return False
        
        current_week = max_week or 44
        current_month = datetime.now().month
        
        self.summary = calculate_summary(self.df, current_week, current_month)
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Create NTH trend
        df_clean = self.df.dropna(subset=["DateObj", "Month", "Week"]).copy()
        self.nth_trend = get_nth_pivot_by_week(df_clean)
        
        return True
    
    def load_from_excel(self, filepath: Path) -> bool:
        """Load dashboard data from existing Excel file."""
        try:
            # Try to load Raw Data sheet
            self.df = pd.read_excel(filepath, sheet_name='Raw Data')
            
            # Try to load Summary sheet
            try:
                self.summary = pd.read_excel(filepath, sheet_name='Summary by Project')
            except:
                self.summary = calculate_summary(self.df)
            
            # Try to load NTH Trend sheet
            try:
                self.nth_trend = pd.read_excel(filepath, sheet_name='NTH Trend by Week', index_col=0)
            except:
                df_clean = self.df.dropna(subset=["DateObj", "Month", "Week"]).copy() if 'DateObj' in self.df.columns else self.df
                self.nth_trend = get_nth_pivot_by_week(df_clean)
            
            self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Excel: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if self.df is None:
            return {}
        
        return {
            "total_records": len(self.df),
            "total_nth": len(self.df),
            "total_qty": self.df['Qty Delivered'].sum() if 'Qty Delivered' in self.df.columns else 0,
            "unique_projects": self.df['Project'].nunique() if 'Project' in self.df.columns else 0,
            "last_updated": self.last_updated
        }
    
    def export(self, output_path: Path) -> bool:
        """Export to Excel file."""
        if self.df is None or self.summary is None:
            return False
        
        raw_df = self.df[["Year", "Day", "Date", "Week", "Project", "Qty Delivered"]].copy()
        return export_dashboard_excel(
            raw_df, self.summary, self.nth_trend or pd.DataFrame(), output_path
        )
