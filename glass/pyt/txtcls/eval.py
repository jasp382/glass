"""
Text classification evaluation
"""

def binary_eval(refTbl, refId, refCol, tstTbl, tstId,
                outTbl=None, tstCol=None):
    """
    Evaluation of a binary classification
    
    When tstCol is None, the script assumes that in tstTbl
    there are only positives
    
    A tabela de referencia deve ter positivos e negativos;
    mas a tabela de teste pode ter so positivos.
    """
    
    import numpy  as np
    import pandas;import math
    from glass.fm  import tbl_to_obj
    from glass.to  import obj_to_tbl
    
    # Data to Pandas Dataframe
    ref_df = tbl_to_obj(
        refTbl, fields=[refId, refCol]
    ) if type(refTbl) != pandas.DataFrame else refTbl[[refId, refCol]]
    tst_df = tbl_to_obj(
        tstTbl, fields=[tstId] if not tstCol else [tstId, tstCol]
    ) if type(refTbl) != pandas.DataFrame else tstTbl[[tstId]] \
        if not tstCol else tstTbl[[tstId, tstCol]]
    
    # Check if refId is equal to tstId; they must be different
    if refId == tstId:
        colRename = {tstId:'tst_fid__'}
        
        # Do the same for refCol and tstCol
        if refCol == tstCol:
            colRename[tstCol] = 'tst_col__'
        
        tst_df.rename(columns=colRename, inplace=True)
        tstId = 'tst_fid__'
        
        if refCol == tstCol:
            tstCol = 'tst_col__'
    
    df = ref_df.merge(
        tst_df, how='left', left_on=refId, right_on=tstId)
    
    # Check if we have a tstCol
    if not tstCol:
        df[tstId].fillna('None', inplace=True)
        
        tstCol = 'cls_tst'
        df[tstCol] = np.where(df[tstId] == 'None', 0, 1)
    
    # Get VP, VN, FP, FN
    df['confusion'] = np.where(
        (df[refCol] == 1) & (df[tstCol] == 1), 'VP', np.where(
            (df[refCol] == 0) & (df[tstCol] == 0), 'VN', np.where(
                (df[refCol] == 1) & (df[tstCol] == 0), 'FN', 'FP'
            )
        )
    )
    
    # tabela sintese
    conf_tbl = pandas.DataFrame()
    conf_tbl['nrows'] = df.groupby(['confusion'])[refId].nunique()
    
    conf_tbl.reset_index(inplace=True)
    
    conf_tbl['percentage'] = (conf_tbl.nrows * 100) / df.shape[0]
    
    # Get some evaluation mesures
    dConf = {}
    
    for row in conf_tbl.to_dict(orient='records'):
        dConf[row['confusion']] = row['nrows']
    
    l = ['VP', 'VN', 'FP', 'FN']
    for i in l:
        if i not in dConf:
            dConf[i] = 0
    
    """
    Error rate

    Error rate (ERR) is calculated as the number of all
    incorrect predictions divided by the total number of
    the dataset. The best error rate is 0.0, whereas the
    worst is 1.0.
    """
    
    ERR = (
        dConf['FP'] + dConf['FN']
    ) / (dConf['VP'] + dConf['VN'] + dConf['FN'] + dConf['FP'])
    
    """
    Accuracy

    Accuracy (ACC) is calculated as the number of all correct
    predictions divided by the total number of the dataset.
    The best accuracy is 1.0, whereas the worst is 0.0. It can
    also be calculated by 1 – ERR.
    """
    
    ACC = (
        dConf['VP'] + dConf['VN']
    ) / (dConf['VP'] + dConf['VN'] + dConf['FN'] + dConf['FP'])
    
    """
    Sensitivity (Recall or True positive rate)
    
    Sensitivity (SN) is calculated as the number of correct
    positive predictions divided by the total number of positives.
    It is also called recall (REC) or true positive rate (TPR).
    The best sensitivity is 1.0, whereas the worst is 0.0.
    """
    
    try:
        SN = dConf['VP'] / (dConf['VP'] + dConf['FN'])
    except:
        SN = -99
    
    """
    Specificity (True negative rate)

    Specificity (SP) is calculated as the number of correct negative
    predictions divided by the total number of negatives. It is
    also called true negative rate (TNR). The best specificity is 1.0,
    whereas the worst is 0.0.
    """
    
    SP = dConf['VN'] / (dConf['VN'] + dConf['FP'])
    
    """
    Precision (Positive predictive value)

    Precision (PREC) is calculated as the number of correct
    positive predictions divided by the total number of positive
    predictions. It is also called positive predictive value (PPV).
    The best precision is 1.0, whereas the worst is 0.0.
    """
    
    PREC = dConf["VP"] / (dConf["VP"] + dConf['FP'])
    
    """
    False positive rate

    False positive rate (FPR) is calculated as the number of
    incorrect positive predictions divided by the total number
    of negatives. The best false positive rate is 0.0 whereas the
    worst is 1.0. It can also be calculated as 1 – specificity.
    """

    FPR = dConf['FP'] / (dConf['VN'] + dConf['FP'])
    
    """
    Matthews correlation coefficient

    Matthews correlation coefficient (MCC) is a correlation
    coefficient calculated using all four values in the
    confusion matrix.
    """
    try:
        MCC = (
            dConf['VP'] * dConf['VN'] - dConf['FP'] * dConf['FN']
        ) / (math.sqrt(
            (dConf['VP'] + dConf['FP']) * (dConf['VP'] + dConf['FN']) *
            (dConf['VN'] + dConf['FP']) * (dConf['VN'] + dConf['FN'])
        ))
    except:
        MCC = -99
    
    """
    F-score

    F-score is a harmonic mean of precision and recall.
    """
    
    F0_5 = ((1 + 0.5**2) * (PREC * SN)) / (0.5**2 * PREC + SN)
    F_1 = (2 * PREC * SN) / (PREC + SN)
    F_2 = (5 * PREC * SN) / (4 * PREC + SN)
    
    evalMeasures = pandas.DataFrame([
        ['Error rate', ERR],
        ['Accuracy', ACC],
        ['Sensitivity', SN],
        ['Specificity', SP],
        ['Precision', PREC],
        ['False positive rate', FPR],
        ['Matthews correlation coefficient', MCC],
        ['F-score 0.5', F0_5],
        ['F-score 1', F_1],
        ['F-score 2', F_2]
    ], columns=['eval_mesure', 'value'])
    
    if outTbl:
        return obj_to_tbl(
            [conf_tbl, evalMeasures, df], outTbl,
            sheetsName=['matrix', 'eval_mesures', 'tbl']
        )
    else:
        return conf_tbl, evalMeasures, df


def model_conf_matrix(tblFile, refCol, clsCol, outMxt):
    """
    Model Evaluation
    """
    
    import pandas        as pd
    from glass.fm         import tbl_to_obj
    from glass.to         import obj_to_tbl
    from sklearn.metrics import confusion_matrix, classification_report
    
    data = tbl_to_obj(tblFile)
    
    data[refCol] = data[refCol].astype(str)
    data[clsCol] = data[clsCol].astype(str)
    
    ref_id = data[[refCol]].drop_duplicates().sort_values(refCol)
    
    conf_mat = confusion_matrix(data[refCol], data[clsCol])
    
    mxt = pd.DataFrame(
        conf_mat, columns=ref_id[refCol].values, index=ref_id[refCol].values)
    mxt.reset_index(inplace=True)
    mxt.rename(columns={'index' : 'confusion_mxt'}, inplace=True)
    
    # Get classification report
    report = classification_report(
        data[refCol], data[clsCol],
        target_names=ref_id[refCol],
        output_dict=True
    )
    
    global_keys = ['accuracy', 'macro avg', 'micro avg', 'weighted avg']
    
    cls_eval = {k : report[k] for k in report if k not in global_keys}
    glb_eval = {k : report[k] for k in report if k in global_keys}
    
    if 'accuracy' in glb_eval:
        glb_eval['accuracy'] = {
            'f1-score' : glb_eval['accuracy'], 'precision' : 0,
            'recall' : 0, 'support' : 0
        }
    
    cls_eval = pd.DataFrame(cls_eval).T
    gbl_eval = pd.DataFrame(glb_eval).T
    
    return obj_to_tbl([gbl_eval, cls_eval, mxt], outMxt, sheetsName=['global', 'report', 'matrix'])

