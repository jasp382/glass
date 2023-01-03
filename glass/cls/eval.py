"""
Evaluation of data classification procedures
"""

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

    df = df.append(new_df, ignore_index=False)

    df.loc['class_area', 'row_area'] = total_area

    df.reset_index(inplace=True)

    df.rename(columns={'index' : cls_col}, inplace=True)

    return df

