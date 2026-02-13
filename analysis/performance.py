# MTR PS-OHLR DUAT - Performance Analysis
"""
Performance Card analysis for weekly productivity tracking.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import io
import base64

logger = logging.getLogger(__name__)


def calculate_performance_metrics(
    df: pd.DataFrame,
    project_code: str,
    target_productivity: float = 3.0
) -> Dict[str, Any]:
    """
    Calculate performance metrics for a project.
    
    Args:
        df: DataFrame with project data
        project_code: Project code to analyze
        target_productivity: Target productivity (qty/NTH)
        
    Returns:
        Dictionary with performance metrics
    """
    # Filter for this project
    proj_df = df[df['Project'].str.upper() == project_code.upper()].copy()
    
    if proj_df.empty:
        return {}
    
    # Ensure we have Year and Week columns
    if 'Year' not in proj_df.columns or 'Week' not in proj_df.columns:
        return {}
    
    # Group by Year-Week
    weekly_data = proj_df.groupby(['Year', 'Week']).agg({
        'Qty Delivered': 'sum'
    }).reset_index()
    
    weekly_data['Year'] = pd.to_numeric(weekly_data['Year'], errors='coerce')
    weekly_data['Week'] = pd.to_numeric(weekly_data['Week'], errors='coerce')
    weekly_data = weekly_data.dropna(subset=['Year', 'Week'])
    
    # Each NTH = 1 record, so count NTH per week
    nth_per_week = proj_df.groupby(['Year', 'Week']).size().reset_index(name='NTH_Count')
    nth_per_week['Year'] = pd.to_numeric(nth_per_week['Year'], errors='coerce')
    nth_per_week['Week'] = pd.to_numeric(nth_per_week['Week'], errors='coerce')
    nth_per_week = nth_per_week.dropna(subset=['Year', 'Week'])
    
    # Merge
    weekly_data = weekly_data.merge(nth_per_week, on=['Year', 'Week'], how='left')
    weekly_data['NTH_Count'] = weekly_data['NTH_Count'].fillna(0)
    
    # Calculate actual productivity per week
    weekly_data['Actual Productivity'] = weekly_data.apply(
        lambda row: row['Qty Delivered'] / row['NTH_Count'] if row['NTH_Count'] > 0 else 0,
        axis=1
    ).round(2)
    
    # Sort by year and week
    weekly_data = weekly_data.sort_values(['Year', 'Week'])
    
    # Calculate metrics
    total_weeks = len(weekly_data)
    weeks_met_target = len(weekly_data[weekly_data['Actual Productivity'] >= target_productivity])
    success_rate = (weeks_met_target / total_weeks * 100) if total_weeks > 0 else 0
    weeks_missed = total_weeks - weeks_met_target
    
    # Calculate current pace (last 12 weeks average)
    recent_data = weekly_data.tail(12)
    if not recent_data.empty and recent_data['NTH_Count'].sum() > 0:
        current_pace = recent_data['Qty Delivered'].sum() / recent_data['NTH_Count'].sum()
    else:
        current_pace = 0
    
    return {
        "weekly_data": weekly_data,
        "total_weeks": total_weeks,
        "weeks_met_target": weeks_met_target,
        "weeks_missed": weeks_missed,
        "success_rate": round(success_rate, 1),
        "target_productivity": target_productivity,
        "current_pace": round(current_pace, 2),
        "avg_productivity": round(weekly_data['Actual Productivity'].mean(), 2) if total_weeks > 0 else 0
    }


def get_recovery_path(
    target_qty: float,
    actual_qty: float,
    remaining_weeks: int,
    current_productivity: float
) -> Dict[str, Any]:
    """
    Calculate recovery path to meet target.
    
    Args:
        target_qty: Total target quantity
        actual_qty: Actual quantity completed
        remaining_weeks: Remaining weeks to deadline
        current_productivity: Current productivity rate
        
    Returns:
        Dictionary with recovery metrics
    """
    remaining_qty = target_qty - actual_qty
    
    if remaining_weeks <= 0:
        return {
            "required_weekly": 0,
            "required_productivity": 0,
            "on_track": actual_qty >= target_qty,
            "projected_completion_week": 0
        }
    
    required_weekly = remaining_qty / remaining_weeks if remaining_weeks > 0 else 0
    
    # Assuming 1 NTH per week average
    required_productivity = required_weekly
    
    # Project when we'll complete at current pace
    if current_productivity > 0:
        weeks_to_complete = remaining_qty / current_productivity
    else:
        weeks_to_complete = float('inf')
    
    return {
        "required_weekly": round(required_weekly, 2),
        "required_productivity": round(required_productivity, 2),
        "on_track": current_productivity >= required_productivity,
        "weeks_to_complete": round(weeks_to_complete, 1) if weeks_to_complete != float('inf') else None
    }


def plot_performance_chart(
    weekly_data: pd.DataFrame,
    target_productivity: float,
    project_code: str,
    output_path: Path = None,
    figsize: Tuple[int, int] = (10, 5)
) -> Optional[str]:
    """
    Plot performance chart.
    
    Args:
        weekly_data: DataFrame with weekly performance data
        target_productivity: Target productivity line
        project_code: Project code for title
        output_path: Optional path to save figure
        figsize: Figure size
        
    Returns:
        Base64 encoded image string if no output_path
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create x-axis labels
    weekly_data = weekly_data.copy()
    weekly_data['Label'] = weekly_data['Year'].astype(int).astype(str) + '-W' + weekly_data['Week'].astype(int).astype(str).str.zfill(2)
    
    x = range(len(weekly_data))
    
    # Bar chart for actual productivity
    colors = ['green' if val >= target_productivity else 'red' 
              for val in weekly_data['Actual Productivity']]
    ax.bar(x, weekly_data['Actual Productivity'], color=colors, alpha=0.7, label='Actual')
    
    # Target line
    ax.axhline(y=target_productivity, color='blue', linestyle='--', linewidth=2, label=f'Target ({target_productivity})')
    
    # Styling
    ax.set_xlabel('Week')
    ax.set_ylabel('Productivity (Qty/NTH)')
    ax.set_title(f'Weekly Performance: {project_code}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # X-axis labels
    n_labels = len(weekly_data)
    step = max(1, n_labels // 10)
    ax.set_xticks(range(0, n_labels, step))
    ax.set_xticklabels([weekly_data['Label'].iloc[i] for i in range(0, n_labels, step)], rotation=45, ha='right')
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return None
    else:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64


def plot_cumulative_progress(
    df: pd.DataFrame,
    project_code: str,
    target_qty: float,
    start_year: int,
    end_year: int,
    output_path: Path = None,
    figsize: Tuple[int, int] = (12, 6)
) -> Optional[str]:
    """
    Plot cumulative progress chart with recovery path.
    
    Args:
        df: DataFrame with project data
        project_code: Project code
        target_qty: Total target quantity
        start_year: Project start year
        end_year: Project end year
        output_path: Optional path to save figure
        figsize: Figure size
        
    Returns:
        Base64 encoded image string if no output_path
    """
    # Filter for this project
    proj_df = df[df['Project'].str.upper() == project_code.upper()].copy()
    
    if proj_df.empty:
        return None
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate cumulative actual by year
    proj_df['Year'] = pd.to_numeric(proj_df['Year'], errors='coerce')
    yearly_qty = proj_df.groupby('Year')['Qty Delivered'].sum().sort_index()
    cumulative_actual = yearly_qty.cumsum()
    
    years = list(range(start_year, end_year + 1))
    
    # Calculate linear target
    total_years = end_year - start_year + 1
    yearly_target = target_qty / total_years
    cumulative_target = [yearly_target * (i + 1) for i in range(total_years)]
    
    # Plot target line (linear)
    ax.plot(years, cumulative_target, 'b--', linewidth=2, label='Plan (Linear)', alpha=0.7)
    
    # Plot actual line
    actual_years = cumulative_actual.index.tolist()
    actual_values = cumulative_actual.values.tolist()
    ax.plot(actual_years, actual_values, 'g-', linewidth=2.5, marker='o', label='Actual')
    
    # Plot recovery path (from current to target)
    if actual_years:
        last_year = actual_years[-1]
        last_value = actual_values[-1]
        if last_year < end_year:
            recovery_years = list(range(int(last_year), end_year + 1))
            recovery_values = np.linspace(last_value, target_qty, len(recovery_years))
            ax.plot(recovery_years, recovery_values, 'r:', linewidth=2, label='Recovery Path')
    
    # Styling
    ax.set_xlabel('Year')
    ax.set_ylabel('Cumulative Quantity')
    ax.set_title(f'Cumulative Progress & Recovery Path: {project_code}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(start_year - 0.5, end_year + 0.5)
    ax.set_ylim(0, target_qty * 1.1)
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        return None
    else:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64


class PerformanceAnalyzer:
    """Performance analysis manager."""
    
    def __init__(self, df: pd.DataFrame = None):
        self.df = df
        self.current_project = None
        self.metrics = None
    
    def set_data(self, df: pd.DataFrame):
        """Set the data DataFrame."""
        self.df = df
    
    def get_available_projects(self) -> List[str]:
        """Get list of projects with data."""
        if self.df is None or self.df.empty:
            return []
        
        if 'Project' in self.df.columns:
            # Get unique projects that start with 'C' (project codes)
            projects = self.df['Project'].unique().tolist()
            return sorted([p for p in projects if str(p).startswith('C')])
        return []
    
    def analyze(
        self,
        project_code: str,
        target_productivity: float = 3.0,
        target_qty: float = None,
        start_year: int = None,
        end_year: int = None
    ) -> Dict[str, Any]:
        """
        Perform full analysis for a project.
        
        Args:
            project_code: Project code
            target_productivity: Target productivity (qty/NTH)
            target_qty: Optional target quantity for recovery path
            start_year: Optional project start year
            end_year: Optional project end year
            
        Returns:
            Dictionary with all analysis results
        """
        if self.df is None or self.df.empty:
            return {}
        
        self.current_project = project_code
        self.metrics = calculate_performance_metrics(
            self.df, project_code, target_productivity
        )
        
        if not self.metrics:
            return {}
        
        result = dict(self.metrics)
        
        # Add recovery path if target info provided
        if target_qty and start_year and end_year:
            current_year = datetime.now().year
            remaining_weeks = (end_year - current_year) * 52
            actual_qty = self.df[self.df['Project'].str.upper() == project_code.upper()]['Qty Delivered'].sum()
            
            result['recovery'] = get_recovery_path(
                target_qty, actual_qty, remaining_weeks, self.metrics.get('current_pace', 0)
            )
        
        return result
    
    def get_weekly_breakdown(self) -> List[Dict[str, Any]]:
        """Get weekly breakdown data for display."""
        if not self.metrics or 'weekly_data' not in self.metrics:
            return []
        
        weekly_df = self.metrics['weekly_data']
        target = self.metrics.get('target_productivity', 3.0)
        
        breakdown = []
        for _, row in weekly_df.iterrows():
            actual = row['Actual Productivity']
            breakdown.append({
                'year': int(row['Year']),
                'week': int(row['Week']),
                'target_rate': target,
                'actual': actual,
                'status': 'met' if actual >= target else 'missed'
            })
        
        return breakdown
