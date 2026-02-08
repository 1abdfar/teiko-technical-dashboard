import pandas as pd
from scipy import stats

def calculate_frequencies(df):
    """Adds total_count and percentage columns."""
    totals = df.groupby('sample_id')['count'].sum().reset_index(name='total_count')
    merged = pd.merge(df, totals, on='sample_id')
    merged['percentage'] = (merged['count'] / merged['total_count']) * 100
    return merged

def run_mann_whitney(df, cell_type, group_col='response', group1='yes', group2='no'):
    """Runs MWU test for a specific cell type between two groups."""
    subset = df[df['cell_type'] == cell_type]
    g1_data = subset[subset[group_col] == group1]['percentage']
    g2_data = subset[subset[group_col] == group2]['percentage']
    
    if len(g1_data) == 0 or len(g2_data) == 0:
        return None, None
        
    stat, p_val = stats.mannwhitneyu(g1_data, g2_data)
    return stat, p_val