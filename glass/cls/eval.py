"""
Evaluation of data classification procedures
"""

import pandas as pd


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

    FPR = d['FP'] / (d['TN'] + d['FP'])
    
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
        F_2 = (5 * PREC * SN) / (4 * PREC + SN)
    except:
        F_2 = -99
    
    eval_measures = pd.DataFrame([
        ['Error rate', ERR],
        ['Accuracy', ACC],
        ['True Positive Rate (Sensitivity)', SN],
        ['True Negative Rate (Specificity)', SP],
        ['Precision', PREC],
        ['False positive rate', FPR],
        ['Matthews correlation coefficient', MCC],
        ['F-score 0.5', F0_5],
        ['F-score 1', F_1],
        ['F-score 2', F_2]
    ], columns=['eval_mesure', 'value'])

    return eval_measures


def mtx_binary_class(tbl, refcol, tstcol, posval, negval, outmtx):
    """
    Produce a confusion matrix for a binary classification

    Ref and Test columns are in the same table
    """

    import numpy as np

    from glass.rd import tbl_to_obj
    from glass.rd.shp import shp_to_obj
    from glass.wt import obj_to_tbl
    from glass.prop import is_shp

    l = ['TP', 'TN', 'FP', 'FN']

    # Check if input is a geospatial file or not
    # And read data
    if is_shp(tbl):
        df = shp_to_obj(tbl)

        df.drop(['geometry'], axis=1, inplace=True)
    else:
        df = tbl_to_obj(tbl)

    df['rid'] = df.index +1

    # Get Confusion field
    # Get TP, TN, FP, FN
    df["confusion"] = np.where(
        (df[refcol] == posval) & (df[tstcol] == posval), 'TP', np.where(
            (df[refcol] == negval) & (df[tstcol] == negval), 'TN', np.where(
                (df[refcol] == negval) & (df[tstcol] == posval), 'FP', 'FN'
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

    # Get evaluation measures
    emeas = calc_confusion_measures(d)

    return obj_to_tbl(
        [mtx, emeas, df], outmtx,
        sheetsName=['matrix', 'metrics', 'data']
    )


def get_measures_for_mtx(mtxdf, cls_col):
    """
    Get Accuracy and Precision matrix for one confusion matrix

    Measures:
    * precision;
    * recall;
    * f1-score;
    * macro-f1-score;
    * weighted-f1-score;

    NOTE: this script assumes that all rows are also columns in the matrix
    """

    import numpy as np
    import pandas as pd

    df = mtxdf.copy()

    # Get class id
    df.set_index(cls_col, inplace=True)

    clsid = df.index.tolist()

    # Check if we have the same number of rows and columns
    cols = list(df.columns.values)
    if len(clsid) != len(cols):
        raise ValueError(
            "Matrix hasn't the same number of rows and columns"
        )

    # Get Row's total area
    df['row_area'] = df.sum(axis=1)

    # Get Precision | User Precision | Erros comissao (inclusao)
    precision = [df.loc[r, r] / df.loc[r, 'row_area'] * 100 for r in clsid]

    df['precision'] = precision

    # Get Recall | Producer Precision | Erros omissao (exclusao)
    cols_sum = [df[i].sum() for i in clsid]

    recall = [df.loc[clsid[i], clsid[i]] / cols_sum[i] * 100 for i in range(len(clsid))]

    # Get Overall accuracy and Kappa values
    total_area = df.row_area.sum()
    prob_a = [i / total_area for i in cols_sum]
    df['prob_b'] = df.row_area / total_area
    prob_b = df.prob_b.tolist()
    df.drop('prob_b', axis=1, inplace=True)

    prob_agree = pd.Series([prob_a[i] * prob_b[i] for i in range(len(prob_a))]).sum()
    overall_accuracy = pd.Series([df.loc[i, i] for i in clsid]).sum() / total_area

    kappa = (overall_accuracy - prob_agree) / (1 - prob_agree)

    # Get F1-Score
    f1scores = [
        2 * (precision[i] * recall[i]) / (precision[i] + recall[i]) for i in range(len(precision))
    ]

    macro_f1 = pd.Series(f1scores).sum() / len(f1scores)
    weigh_f1 = pd.Series([cols_sum[i] * f1scores[i] for i in range(len(cols_sum))]).sum() / total_area

    # Update Matrix with new measures
    col_percentage = [i / total_area * 100 for i in cols_sum]

    new_df = pd.DataFrame([
        cols_sum, col_percentage, recall, f1scores,
        [overall_accuracy * 100] + [np.nan for i in range(1, len(df.columns.values))],
        [kappa] + [np.nan for i in range(1, len(df.columns.values))],
        [macro_f1] + [np.nan for i in range(1, len(df.columns.values))],
        [weigh_f1] + [np.nan for i in range(1, len(df.columns.values))]
    ], index=[
        'class_area', 'class_percentage', 'recall', 'f1-score',
        'overall_accuracy', 'kappa', 'macro-f1', 'weighted-f1'
    ], columns=df.columns.values)

    df = pd.concat([df, new_df], ignore_index=True)

    df.loc['class_area', 'row_area'] = total_area

    df.reset_index(inplace=True)

    df.rename(columns={'index' : cls_col}, inplace=True)

    return df

