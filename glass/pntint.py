"""
Point Intersection
"""

"""
Intersections based on direction
"""

def direct_intersection(PA, PB, D_AX, D_BX):
    """
    Interseccao directa aplicada a um unico par de coordenadas
    """
    
    import math as mt
    
    PA_X, PA_Y = PA; PB_X, PB_Y = PB
    
    PQ_NUM = (PB_X - PA_X) - (PB_Y - PA_Y) * mt.tan(mt.radians(D_BX))
    
    PQ_DEN = mt.tan(mt.radians(D_AX)) - mt.tan(mt.radians(D_BX))
    
    PQ = (PQ_NUM / PQ_DEN) + PA_X
    
    MQ = ((PQ - PA_Y) * m.tan(m.radians(D_AX))) + PA_X
    
    return MQ, PQ


def lateral_intersection(PA, PB, D_AX, D_BX):
    """
    Interseccao lateral aplica a um unico par de coordenadas
    """
    
    import math as mt
    
    PA_X, PA_Y = PA; PB_X, PB_Y = PB
    
    MQ_NUM = (PB_Y - PA_Y) - (PB_X - PA_X) * (
        mt.cos(mt.radians(D_BX)) / mt.sin(mt.radians(D_BX)))
    
    MQ_DEN = (mt.cos(mt.radians(D_AX)) / mt.sin(mt.radians(D_AX))) - (
        mt.cos(mt.radians(D_AX)) / mt.sin(mt.radians(D_BX)))
    
    MQ = (MQ_NUM / MQ_DEN) + PA_X
    
    PQ = ((MQ - PA_X) * (
        mt.cos(mt.radians(D_AX)) / mt.sin(mt.radians(D_AX)))) + PA_Y
    
    return MQ, PQ


def df_direct_intersection(df, resCol, pntAX, pntAY, pntBX, pntBY, dir_aq,
                           dir_bq):
    """
    Interseccao directa calculada automaticamente para todas as linhas de um
    DataFrame do Pandas
    """
    
    import numpy as np
    
    resCol_P = resCol + '_P'
    resCol_M = resCol + '_M'
    
    df[resCol_P] = (
        (df[pntBX] - df[pntAX]) - (df[pntBY] - df[pntAY]) * np.tan(
            np.radians(df[dir_bq]))
    ) / (
        np.tan(np.radians(df[dir_aq])) - np.tan(np.radians(df[dir_bq]))
    ) + df[pntAY]
    
    df[resCol_M] = (
        (df[resCol_P] - df[pntAY]) * np.tan(np.radians(df[dir_aq]))
    ) + df[pntAX]
    
    return df


def df_lateral_intersection(df, resCol, pntAX, pntAY, pntBX, pntBY, dir_aq,
                            dir_bq):
    """
    Interseccao lateral calculada automaticamente para todas as linhas de um
    DataFrame do Pandas
    """
    
    import numpy as np
    
    resCol_P = resCol + '_P'
    resCol_M = resCol + '_M'
    
    df[resCol_M] = (
        (df[pntBY] - df[pntAY]) - (df[pntBX] - df[pntAX]) * (
            np.cos(np.radians(df[dir_bq])) / np.sin(np.radians(df[dir_bq]))
        )
    ) / (
        (
            np.cos(np.radians(df[dir_aq])) / np.sin(np.radians(df[dir_aq]))
        ) - (
            np.cos(np.radians(df[dir_bq])) / np.sin(np.radians(df[dir_bq]))
        )
    ) + df[pntAX]
    
    df[resCol_P] = ((df[resCol_M] - df[pntAX]) * (
        np.cos(np.radians(df[dir_aq])) / np.sin(np.radians(df[dir_aq]))
    )) + df[pntAY]
    
    return df

