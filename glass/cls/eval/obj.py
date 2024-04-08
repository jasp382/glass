"""
Compute confusion matrix and quality measures
without files
"""

import pandas as pd
import numpy as np

from glass.rd import tbl_to_obj

def calc_confusion_measures(d):
    """
    Calculate confusion measures from dict:
    d = {
        'TP': number of true positives,
        'TN': number of true negatives,
        'FP': number of false positives,
        'FN': number of false negatives,
    }
    """

    import math

    """
    Error rate

    Error rate (ERR) is calculated as the number of all
    incorrect predictions divided by the total number of
    the dataset. The best error rate is 0.0, whereas the
    worst is 1.0.
    """

    ERR = (
        d['FP'] + d['FN']
    ) / (d['TP'] + d['TN'] + d['FN'] + d['FP'])
    
    """
    Accuracy

    Accuracy (ACC) is calculated as the number of all correct
    predictions divided by the total number of the dataset.
    The best accuracy is 1.0, whereas the worst is 0.0. It can
    also be calculated by 1 – ERR.
    """
    
    ACC = (
        d['TP'] + d['TN']
    ) / (d['TP'] + d['TN'] + d['FN'] + d['FP'])

    """
    Weighted accuracy
    """

    ACC_W = (1/2) * ((d["TP"] / (d["TP"] + d["FN"])) + (
        d["TN"] / (d["TN"] + d["FP"])
    ))
    
    """
    Sensitivity (Recall or True positive rate)
    
    Sensitivity (SN) is calculated as the number of correct
    positive predictions divided by the total number of positives.
    It is also called recall (REC) or true positive rate (TPR).
    The best sensitivity is 1.0, whereas the worst is 0.0.
    """
    
    try:
        SN = d['TP'] / (d['TP'] + d['FN'])
    except:
        SN = -99
    
    """
    Specificity (True negative rate)

    Specificity (SP) is calculated as the number of correct negative
    predictions divided by the total number of negatives. It is
    also called true negative rate (TNR). The best specificity is 1.0,
    whereas the worst is 0.0.
    """
    
    try:
        SP = d['TN'] / (d['TN'] + d['FP'])
    except:
        SP = -99
    
    """
    Precision (Positive predictive value)

    Precision (PREC) is calculated as the number of correct
    positive predictions divided by the total number of positive
    predictions. It is also called positive predictive value (PPV).
    The best precision is 1.0, whereas the worst is 0.0.
    """
    
    try:
        PREC = d["TP"] / (d["TP"] + d['FP'])
    except:
        PREC = -99
    
    """
    False positive rate

    False positive rate (FPR) is calculated as the number of
    incorrect positive predictions divided by the total number
    of negatives. The best false positive rate is 0.0 whereas the
    worst is 1.0. It can also be calculated as 1 – specificity.
    """

    try:
        FPR = d['FP'] / (d['TN'] + d['FP'])
    except:
        FPR = -99
    
    """
    Matthews correlation coefficient

    Matthews correlation coefficient (MCC) is a correlation
    coefficient calculated using all four values in the
    confusion matrix.
    """
    try:
        MCC = (
            d['TP'] * d['TN'] - d['FP'] * d['FN']
        ) / (math.sqrt(
            (d['TP'] + d['FP']) * (d['TP'] + d['FN']) *
            (d['TN'] + d['FP']) * (d['TN'] + d['FN'])
        ))
    except:
        MCC = -99
    
    """
    F-score

    F-score is a harmonic mean of precision and recall.
    """
    
    try:
        F0_5 = ((1 + 0.5**2) * (PREC * SN)) / (0.5**2 * PREC + SN)
    except:
        F0_5 = -99
    
    try:
        F_1 = (2 * PREC * SN) / (PREC + SN)
    except:
        F_1 = -99
    
    try:
        F1_2 = 2 * ((PREC * SN) / (PREC + SN))
    
    except:
        F1_2 = -99
    
    try:
        F_2 = (5 * PREC * SN) / (4 * PREC + SN)
    except:
        F_2 = -99
    
    # F1-SCORE from sk-learn
    try:
        F1_SK = (2 * d["TP"]) / (2 * d["TP"] + d["FP"] + d["FN"])
    except:
        F1_SK = -99
    
    eval_measures = pd.DataFrame([
        ['Error rate', ERR],
        ['Accuracy', ACC],
        ["Weighted Accuracy" , ACC_W],
        ['True Positive Rate (Sensitivity)', SN],
        ['True Negative Rate (Specificity)', SP],
        ['Precision', PREC],
        ['False positive rate', FPR],
        ['Matthews correlation coefficient', MCC],
        ['F-score 0.5', F0_5],
        ['F-score 1', F_1],
        ['F-score 1 (2)', F1_2],
        ['F1-score - sklearn', F1_SK],
        ['F-score 2', F_2]
    ], columns=['eval_mesure', 'value'])

    return eval_measures


def df_bincls_to_mtx(df, refcol, tstcol, posval, negval, cls_df=None, df_pk=None, df_fk=None):
    """
    Pandas Dataframe with results of a binary classification to 
    confusion matrix
    """

    if not isinstance(df, pd.DataFrame):
        df = tbl_to_obj(df)

    l = ['TP', 'TN', 'FP', 'FN']

    # Check if classification results are in another table
    if type(cls_df) == pd.DataFrame and df_pk and df_fk:
        if df_pk == df_fk:
            _df_fk = f'{df_fk}_fk'
            cls_df.rename(columns={df_fk : _df_fk}, inplace=True)
        
        else:
            _df_fk = df_fk
        
        if refcol == tstcol:
            _tstcol = f'{tstcol}_test'

            df.rename(columns={tstcol : _tstcol}, inplace=True)
        
        else:
            _tstcol = tstcol

            if refcol in cls_df.columns.values:
                cls_df.drop([refcol], axis=1, inplace=True)
            
            if tstcol in df.columns.values:
                df.drop([tstcol], axis=1, inplace=True)
        
        df = df.merge(cls_df, how='inner', left_on=df_pk, right_on=_df_fk)
    
    else:
        _tstcol = tstcol
    
    df['rid'] = df.index +1
    
    # Filter dataframe
    # Remove nulls
    # Mantain only positive and negative values
    df = df[df[refcol].isin([posval, negval])]
    df = df[df[_tstcol].isin([posval, negval])]

    df[refcol]  = df[refcol].astype(int)
    df[_tstcol] = df[_tstcol].astype(int)
    

    # Get Confusion field
    # Get TP, TN, FP, FN
    df["confusion"] = np.where(
        (df[refcol] == posval) & (df[_tstcol] == posval), 'TP', np.where(
            (df[refcol] == negval) & (df[_tstcol] == negval), 'TN', np.where(
                (df[refcol] == negval) & (df[_tstcol] == posval), 'FP', 'FN'
            )
        )
    )

    # Table with TP, TN, FP, FN frequencies
    conftbl = pd.DataFrame()

    conftbl['nrows'] = df.groupby(['confusion'])['rid'].nunique()

    conftbl.reset_index(inplace=True)

    d = {}

    for idx, row in conftbl.iterrows():
        d[row['confusion']] = row.nrows
    
    for i in l:
        if i not in d:
            d[i] = 0
    
    # Get confusion matrix
    mtx = pd.DataFrame([
        [d['TP'], d['FP']],
        [d['FN'], d['TN']]
    ], columns=[posval, negval])

    mtx.insert(0, 'class', pd.Series([posval, negval]))

    # Get evaluation measures
    emeas = calc_confusion_measures(d)

    return mtx, emeas


def confmtx_fmdf(df, refcol, classcol, class_labels):
    """
    Confusion Matrix from table
    """

    from glass.cls.eval import get_measures_for_mtx

    # Get classes in both arrays
    refcls = df[refcol].unique()
    clscls = df[classcol].unique()
    refcls_ = list(np.sort(np.unique(np.append(refcls, clscls))))

    # Matrix classes
    mtx_coords = {}

    i = 1
    for v in refcls_:
        for v_ in refcls_:
            mtx_coords[(v, v_)] = i

            i += 1
    
    df['confcoord'] = 0

    for k in mtx_coords:
        df['confcoord'] = np.where(
            (df[refcol] == k[1]) & (df[classcol] == k[0]),
            mtx_coords[k], df.confcoord
        )
    
    # Group by DF
    id_mtx = list(df.confcoord.unique())
    freq_mtxid = pd.DataFrame({
        'freqmtxid' : df.groupby(['confcoord'])['confcoord'].agg('count')
    })

    # Create final matrix
    mtx_values = {}
    for k in mtx_coords:
        if mtx_coords[k] in id_mtx:
            mtx_values[k] = freq_mtxid.loc[mtx_coords[k]].freqmtxid
        
        else:
            mtx_values[k] = 0
    
    mtx_lst = []
    for v in refcls_:
        r = []
        for v_ in refcls_:
            r.append(mtx_values[(v, v_)])
        mtx_lst.append(r)
    
    labels = [class_labels[c] for c in refcls_]

    mtx_df = pd.DataFrame(mtx_lst, columns=labels)

    mtx_df['class'] = labels

    out_df = get_measures_for_mtx(mtx_df, 'class')
    
    return out_df

