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

def get_part4_answers(df):
    """
    Analyzes baseline melanoma PBMC samples treated with miraclib.
    
    Returns counts by project, response status, gender, and average
    B-cell count for male responders.
    """
    subset = df[
        (df['condition'] == 'melanoma') & 
        (df['sample_type'] == 'PBMC') & 
        (df['time_from_treatment_start'] == 0) & 
        (df['treatment'] == 'miraclib')
    ]
    # TODO: add validation for case-sensitive filtering(?)
    
    samples_per_proj = subset[['sample_id', 'project']].drop_duplicates()['project'].value_counts().to_dict()
    unique_subs = subset[['subject', 'response', 'sex']].drop_duplicates()
    response_counts = unique_subs['response'].value_counts().to_dict()
    sex_counts = unique_subs['sex'].value_counts().to_dict()
    
    male_resp_b_cells = subset[
        (subset['sex'] == 'M') & 
        (subset['response'] == 'yes') & 
        (subset['cell_type'] == 'b_cell')
    ]['count'].mean()
    
    return {
        "samples_per_proj": samples_per_proj,
        "response_counts": response_counts,
        "sex_counts": sex_counts,
        "avg_b_cell_male_responder": male_resp_b_cells
    }