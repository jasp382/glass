"""
Statistic in Dataframes
"""

def df_to_freqdf(df, col):
    """
    Dataframe To frequencies DataFrame
    """
    
    import pandas
    
    freq = df[col].value_counts()
    
    freq = pandas.DataFrame(freq)
    freq.reset_index(inplace=True)
    freq.rename(columns={col : 'count', 'index' : col}, inplace=True)
    
    Total = freq['count'].sum()
    freq['percentage'] = freq['count'] / Total * 100 
    
    return freq


def get_intervals(df, col, nint, method='EQUAL_INTERVALS'):
    """
    Return intervals for one column
    
    methods:
    * EQUAL_INTERVALS;
    * QUANTILE;
    """
    
    method = 'EQUAL_INTERVALS' if not method else method
    
    if method == 'EQUAL_INTERVALS':
        min_val = df[col].min()
        max_val = df[col].max()
        
        amp_int = (max_val - min_val) / nint
        intervals = []
        for i in range(nint-1):
            if not i:
                intervals.append(round(min_val + amp_int, 3))
            else:
                intervals.append(round(intervals[i-1] + amp_int, 3))
    
    elif method == 'QUANTILE':
        Q = []
        S = 0
        
        for i in range(nint - 1):
            S += 1/nint
            Q.append(S)
        
        intervals = [round(
            i, 3
        ) for i in df[col].quantile(Q, interpolation="linear")]
    
    return intervals

