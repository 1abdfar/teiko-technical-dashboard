import pandas as pd
from src.analysis import calculate_frequencies

def test_calculate_frequencies():
    # Mock data
    data = {
        'sample_id': ['s1', 's1', 's2', 's2'],
        'cell_type': ['b_cell', 't_cell', 'b_cell', 't_cell'],
        'count': [10, 90, 20, 80]
    }
    df = pd.DataFrame(data)
    
    result = calculate_frequencies(df)
    
    s1_b = result[(result['sample_id']=='s1') & (result['cell_type']=='b_cell')]['percentage'].values[0]
    assert s1_b == 10.0    
    s2_t = result[(result['sample_id']=='s2') & (result['cell_type']=='t_cell')]['percentage'].values[0]
    assert s2_t == 80.0