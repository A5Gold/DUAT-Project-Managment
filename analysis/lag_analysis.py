# MTR PS-OHLR DUAT - Lag/Lead Analysis
"""
NTH Lag/Lead analysis for project progress tracking.
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def get_status(nth_lag_lead: float, t_func=None) -> Tuple[str, str]:
    """
    Determine project status based on NTH lag/lead value.
    
    Args:
        nth_lag_lead: NTH lag/lead value (positive=ahead, negative=behind)
        t_func: Translation function
        
    Returns:
        Tuple of (status_text, status_color)
    """
    t = t_func if t_func else lambda x: x
    
    if nth_lag_lead <= -10:
        return t("lag_urgent"), "red"
    elif nth_lag_lead <= -5:
        return t("lag_behind"), "orange"
    elif nth_lag_lead < 0:
        return t("lag_slight"), "yellow"
    elif nth_lag_lead < 5:
        return t("lag_on_track"), "green"
    else:
        return t("lag_ahead"), "blue"


def load_project_master(filepath: Path) -> Tuple[pd.DataFrame, Dict[str, str], Dict[str, float]]:
    """
    Load project master Excel file.
    
    Args:
        filepath: Path to the Excel file
        
    Returns:
        Tuple of (project_master_df, project_descriptions, target_qty_map)
    """
    df = pd.read_excel(filepath)
    
    # Find required columns (case-insensitive search)
    col_mapping = {}
    for col in df.columns:
        col_lower = str(col).lower().strip()
        col_str = str(col).strip()
        
        # Project No column
        if col_lower == 'project no' or col_lower == 'projectno' or col_lower == 'project number':
            col_mapping['project_no'] = col
        elif 'project no' in col_lower and 'project_no' not in col_mapping:
            col_mapping['project_no'] = col
        
        # Description - look for "One Line Title" specifically first
        elif col_lower == 'one line title' or col_str == 'One Line Title':
            col_mapping['description'] = col
        elif 'one line' in col_lower and 'title' in col_lower:
            col_mapping['description'] = col
        
        # Only use 'description' or 'title' if we haven't found 'One Line Title'
        elif 'description' not in col_mapping:
            if col_lower == 'description' or col_lower == 'title':
                col_mapping['description'] = col
            elif col_lower == 'project title' or col_lower == 'project description':
                col_mapping['description'] = col
        
        # Start Date
        elif 'start' in col_lower and 'date' in col_lower:
            col_mapping['start_date'] = col
        elif col_lower == 'start date' or col_lower == 'startdate':
            col_mapping['start_date'] = col
        
        # Finish/End Date
        elif 'finish' in col_lower and 'date' in col_lower:
            col_mapping['finish_date'] = col
        elif 'end' in col_lower and 'date' in col_lower:
            col_mapping['finish_date'] = col
        elif col_lower == 'finish date' or col_lower == 'end date':
            col_mapping['finish_date'] = col
        
        # Target Quantity
        elif 'target' in col_lower and ('quantity' in col_lower or 'qty' in col_lower):
            col_mapping['target_qty'] = col
        elif col_lower == 'target quantity' or col_lower == 'target qty':
            col_mapping['target_qty'] = col
    
    # Check for Project No column (required)
    if 'project_no' not in col_mapping:
        if len(df.columns) >= 3:
            col_mapping['project_no'] = df.columns[2]  # Column C (index 2)
        else:
            raise ValueError("Could not find 'Project No' column in Excel file")
    
    # Extract project data
    projects = []
    project_descriptions = {}
    target_qty_map = {}
    
    for idx, row in df.iterrows():
        project_no = str(row.get(col_mapping.get('project_no', ''), '')).strip()
        
        if not project_no or project_no == 'nan' or project_no == '':
            continue
        
        projects.append(project_no)
        
        # Get description
        if 'description' in col_mapping:
            desc = str(row.get(col_mapping['description'], '')).strip()
            if desc and desc != 'nan':
                project_descriptions[project_no] = desc
        
        # Get Target Quantity
        if 'target_qty' in col_mapping:
            try:
                val = row.get(col_mapping['target_qty'])
                if pd.notna(val) and str(val).strip() != '' and str(val).strip() != 'nan':
                    target_qty_map[project_no] = float(val)
            except Exception:
                pass
    
    # Build project_master DataFrame
    project_master_rows = []
    for idx, row in df.iterrows():
        project_no = str(row.get(col_mapping.get('project_no', ''), '')).strip()
        if not project_no or project_no == 'nan' or project_no == '':
            continue
        
        # Get description
        desc = ''
        if 'description' in col_mapping:
            desc = str(row.get(col_mapping['description'], '')).strip()
            if desc == 'nan':
                desc = ''
        
        # Get dates
        start_date = None
        end_date = None
        if 'start_date' in col_mapping:
            try:
                start_date = pd.to_datetime(row.get(col_mapping['start_date']), dayfirst=True)
            except:
                pass
        if 'finish_date' in col_mapping:
            try:
                end_date = pd.to_datetime(row.get(col_mapping['finish_date']), dayfirst=True)
            except:
                pass
        
        project_master_rows.append({
            'Project No': project_no,
            'Title': desc,
            'Start Date': start_date,
            'End Date': end_date,
        })
    
    project_master_df = pd.DataFrame(project_master_rows)
    
    return project_master_df, project_descriptions, target_qty_map


def calculate_nth_lag_lead(
    project_master: pd.DataFrame,
    config: Dict[str, Dict],
    actual_qty_map: Dict[str, float],
    t_func=None
) -> List[Dict[str, Any]]:
    """
    Calculate lag/lead for all projects.
    
    Args:
        project_master: DataFrame with project info
        config: Configuration dict with target_qty, productivity, skip per project
        actual_qty_map: Map of project -> actual quantity delivered
        t_func: Translation function
        
    Returns:
        List of result dictionaries
    """
    if project_master is None or project_master.empty:
        return []
    
    results = []
    today = datetime.now()
    
    for _, row in project_master.iterrows():
        proj_no = str(row['Project No']).strip()
        title = row.get('Title', '') if 'Title' in row else ''
        start_date = row['Start Date']
        end_date = row['End Date']
        
        # Get config for this project
        proj_config = config.get(proj_no, {})
        if proj_config.get("skip", False):
            continue
        
        # Get target qty and productivity
        target_qty = proj_config.get("target_qty")
        productivity = proj_config.get("productivity", 3.0)
        
        # Skip if no valid target qty
        if target_qty is None or target_qty == "N/A" or target_qty == "":
            continue
        
        try:
            target_qty = float(target_qty)
            productivity = float(productivity) if productivity else 3.0
        except (ValueError, TypeError):
            continue
        
        # Calculate project duration
        if pd.notna(start_date) and pd.notna(end_date):
            total_days = (end_date - start_date).days
            elapsed_days = max(0, (today - start_date).days)
            total_weeks = total_days / 7 if total_days > 0 else 1
            elapsed_weeks = elapsed_days / 7
            
            # Linear progress percentage (time-based)
            target_progress_pct = min(100, (elapsed_days / total_days) * 100) if total_days > 0 else 0
            
            # Target quantity to date (linear assumption)
            target_qty_to_date = (target_progress_pct / 100) * target_qty
            
            # Get actual quantity from dashboard
            actual_qty = actual_qty_map.get(proj_no, 0)
            
            # Calculate actual progress percentage
            actual_progress_pct = (actual_qty / target_qty * 100) if target_qty > 0 else 0
            
            # Calculate NTH Lag/Lead
            qty_difference = actual_qty - target_qty_to_date
            nth_lag_lead = round(qty_difference / productivity, 1) if productivity > 0 else 0
            
            # Determine status and color
            status, status_color = get_status(nth_lag_lead, t_func)
            
            results.append({
                "Project": proj_no,
                "Title": title,
                "Start Date": start_date.strftime('%Y-%m-%d') if pd.notna(start_date) else '',
                "End Date": end_date.strftime('%Y-%m-%d') if pd.notna(end_date) else '',
                "Target Qty": target_qty,
                "Actual Qty": actual_qty,
                "Target % (Linear)": round(target_progress_pct, 1),
                "Progress %": round(actual_progress_pct, 1),
                "Productivity": productivity,
                "NTH Lag/Lead": nth_lag_lead,
                "Status": status,
                "Status Color": status_color
            })
    
    return results


def export_lag_report(results_df: pd.DataFrame, output_path: Path) -> bool:
    """
    Export lag analysis results to Excel.
    
    Args:
        results_df: Results DataFrame
        output_path: Output file path
        
    Returns:
        True if successful
    """
    try:
        results_export = results_df.copy()
        
        # Remove internal columns
        if 'Status Color' in results_export.columns:
            results_export = results_export.drop(columns=['Status Color'])
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            results_export.to_excel(writer, sheet_name='Lag Analysis', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Lag Analysis']
            for idx, col in enumerate(results_export.columns):
                max_length = max(
                    results_export[col].astype(str).map(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 20)
        
        return True
    except Exception as e:
        logger.error(f"Error exporting lag report: {e}")
        return False


class LagAnalyzer:
    """High-level lag analysis manager."""
    
    def __init__(self):
        self.project_master = None
        self.projects = []
        self.project_descriptions = {}
        self.target_qty_map = {}
        self.productivity_map = {}
        self.productivity_source = {}
        self.config = {}
        self.results = None
        self.last_calculated = None
    
    def load_project_master(self, filepath: Path, summary_df: pd.DataFrame = None) -> bool:
        """
        Load project master from Excel file.
        
        Args:
            filepath: Path to Excel file
            summary_df: Optional summary DataFrame for productivity matching
            
        Returns:
            True if successful
        """
        try:
            self.project_master, self.project_descriptions, self.target_qty_map = \
                load_project_master(filepath)
            
            self.projects = self.project_master['Project No'].tolist()
            
            # Initialize config for each project
            for proj_no in self.projects:
                if proj_no not in self.config:
                    self.config[proj_no] = {
                        "target_qty": self.target_qty_map.get(proj_no),
                        "productivity": 3.0,
                        "source": "default",
                        "skip": False
                    }
                elif proj_no in self.target_qty_map:
                    self.config[proj_no]["target_qty"] = self.target_qty_map[proj_no]
            
            # Match productivity from summary if available
            if summary_df is not None:
                self._match_productivity(summary_df)
            
            return True
        except Exception as e:
            logger.error(f"Error loading project master: {e}")
            return False
    
    def _match_productivity(self, summary_df: pd.DataFrame):
        """Match productivity from dashboard summary data."""
        for _, row in summary_df.iterrows():
            proj_id = None
            for col_name in ['Project', 'project', 'PROJECT', 'Project No', 'project_no']:
                if col_name in row.index:
                    proj_id = str(row[col_name]).strip()
                    break
            
            if not proj_id:
                continue
            
            # Get Qty per NTH - this is the productivity value
            qty_per_nth = None
            for col_name in ['Qty per NTH', 'Qty/NTH', 'qty_per_nth', 'Productivity']:
                if col_name in row.index:
                    qty_per_nth = row[col_name]
                    break
            
            if proj_id and qty_per_nth is not None and not pd.isna(qty_per_nth):
                try:
                    self.productivity_map[proj_id] = round(float(qty_per_nth), 2)
                    self.productivity_source[proj_id] = "daily_report"
                    
                    # Update config
                    if proj_id in self.config:
                        self.config[proj_id]["productivity"] = self.productivity_map[proj_id]
                        self.config[proj_id]["source"] = "daily_report"
                except (ValueError, TypeError):
                    pass
    
    def calculate(self, actual_qty_map: Dict[str, float], t_func=None) -> bool:
        """
        Calculate lag/lead analysis.
        
        Args:
            actual_qty_map: Map of project -> actual quantity
            t_func: Translation function
            
        Returns:
            True if results were calculated
        """
        if self.project_master is None or self.project_master.empty:
            return False
        
        results = calculate_nth_lag_lead(
            self.project_master,
            self.config,
            actual_qty_map,
            t_func
        )
        
        if results:
            self.results = pd.DataFrame(results)
            self.last_calculated = datetime.now().strftime("%Y-%m-%d %H:%M")
            return True
        
        self.results = None
        return False
    
    def export(self, output_path: Path) -> bool:
        """Export results to Excel."""
        if self.results is None:
            return False
        return export_lag_report(self.results, output_path)
