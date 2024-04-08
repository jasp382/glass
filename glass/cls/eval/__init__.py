"""
Evaluation of data classification procedures
"""

import os
import pandas as pd
import numpy as np

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from functools import partial
import tempfile
import csv
import traceback

from glass.cls.eval.obj import df_bincls_to_mtx
from glass.it.db import multixlsx_to_onetable
from glass.wt import obj_to_tbl
from glass.rd import tbl_to_obj
from glass.sql.q import q_to_obj
from glass.sql.db import create_pgdb
from glass.pys.oss import fprop, lst_ff



def mtx_binary_class(tbl, refcol, tstcol, posval, negval, outmtx,
                     clstable=None, tbl_pk=None, tbl_fk=None):
    """
    Produce a confusion matrix for a binary classification

    Ref and Test columns are in the same table
    """

    from glass.rd.shp       import shp_to_obj
    from glass.prop.df      import is_shp
    from glass.cls.eval.obj import df_bincls_to_mtx

    # Check if input is a geospatial file or not
    # And read data
    if is_shp(tbl):
        df = shp_to_obj(tbl)

        df.drop(['geometry'], axis=1, inplace=True)
    else:
        df = tbl_to_obj(tbl)

    # Check if classification results are in another table
    if clstable and tbl_pk and tbl_fk:
        if is_shp(clstable):
            cls_df = shp_to_obj(clstable)

            cls_df.drop('geometry', axis=1, inplace=True)
        else:
            cls_df = tbl_to_obj(clstable)
    
    else:
        cls_df = None
    
    mtx, emeas = df_bincls_to_mtx(
        df, refcol, tstcol, posval, negval,
        cls_df=cls_df, df_pk=tbl_pk, df_fk=tbl_fk
    )

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

    df = pd.concat([df, new_df], ignore_index=False)

    df.loc['total_area', 'row_area'] = total_area

    df.reset_index(inplace=True)

    df.rename(columns={'index' : cls_col}, inplace=True)

    return df



def compile_binary_mtxs(tbls:list[str], refcol:str, tstcol:str, outres:str) -> str:
    """
    Compute several binary confusion matrices and 
    present all results in one table
    """

    ftbl = []

    cols = [
        'exp', 'test_table', "TP", "TN",
        "FP", "FN", "ACC", "ACC_W", "TPR", "TNR", "precision",
        "FPR", "f1-score", "F1-score-2", "F1-score-sk"
    ]

    for i, t in enumerate(tbls):
        # Create confusion matrices
    
        tdf = tbl_to_obj(t)
        mtx, meas = df_bincls_to_mtx(tdf, refcol, tstcol, 1, 0)

        row = [
            i + 1,
            fprop(t, 'fn'),
            # True Positives
            mtx.loc[0, 1],
            # True Negatives
            mtx.loc[1, 0],
            # False Positives
            mtx.loc[0, 0],
            # False negatives
            mtx.loc[1, 1],
            # ACC
            meas.loc[1, 'value'],
            # ACC - Weighted,
            meas.loc[2, 'value'],
            # TPR
            meas.loc[3, 'value'],
            # TNR
            meas.loc[4, 'value'],
            # Precision
            meas.loc[5, 'value'],
            # FPR
            meas.loc[6, 'value'],
            # F1 Score
            meas.loc[9, 'value'],
            meas.loc[10, 'value'],
            meas.loc[11, 'value']
        ]

        ftbl.append(row)
    
    fdf = pd.DataFrame(ftbl, columns=cols)

    obj_to_tbl(fdf, outres)

    return outres


def _process_single_table(tpath, eidx, refcol, tstcol):
    """
    Processa um ficheiro/tabela e devolve uma linha pronta (ou uma tupla (False, error_msg)).
    Devolve: (True, row_dict) em sucesso, ou (False, {'error': str, 'file': tpath})
    """

    try:
        tdf = tbl_to_obj(tpath, fields=[refcol, tstcol])

        mtx, meas = df_bincls_to_mtx(tdf, refcol, tstcol, 1, 0)

        row = {
            'exp': eidx,
            'test_table': fprop(tpath, 'fn'),
            'TP': int(mtx.loc[0, 1]),
            'TN': int(mtx.loc[1, 0]),
            'FP': int(mtx.loc[0, 0]),
            'FN': int(mtx.loc[1, 1]),
            'ACC': float(meas.loc[1, 'value']),
            'ACC_W': float(meas.loc[2, 'value']),
            'TPR': float(meas.loc[3, 'value']),
            'TNR': float(meas.loc[4, 'value']),
            'precision': float(meas.loc[5, 'value']),
            'FPR': float(meas.loc[6, 'value']),
            'f1-score': float(meas.loc[9, 'value']),
            'F1-score-2': float(meas.loc[10, 'value']),
            'F1-score-sk': float(meas.loc[11, 'value'])
        }

        return True, row
    
    except Exception as e:
        tb = traceback.format_exc()
        return False, {'file': tpath, 'error': str(e), 'traceback': tb}


def compile_binary_mtxs_parallel(tbls: list[str],
                                 refcol: str,
                                 tstcol: str,
                                 outres: str,
                                 max_workers: int | None = None,
                                 use_threads: bool = False):
    """
    Versão paralela de compile_binary_mtxs.
    - tbls: lista de paths (ficheiros Excel, CSV, etc.)
    - refcol, tstcol: nomes das colunas
    - outres: path do ficheiro de saída (CSV será criado; se write_via_obj_to_tbl=True, tentamos usar obj_to_tbl no final)
    - posval, negval: valores de classe positiva/negativa
    - max_workers: None -> usa (os.cpu_count() or 4)
    - batch_write: escreve no disco em batches (para não manter 7GB em memória)
    - use_threads: se True usa ThreadPoolExecutor (útil se glass.* não for picklable)
    - write_via_obj_to_tbl: se True, tenta converter CSV final para o formato esperado por obj_to_tbl (usando obj_to_tbl)
    Retorna: outres (path)
    """

    # Colunas do resultado final (igual ao original)
    cols = [
        'exp', 'test_table', "TP", "TN",
        "FP", "FN", "ACC", "ACC_W", "TPR", "TNR", "precision",
        "FPR", "f1-score", "F1-score-2", "F1-score-sk"
    ]

    if max_workers is None:
        max_workers = max(1, os.cpu_count() or 4) - 1
    
    Exeutor = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

    worker_partial = partial(
        _process_single_table, refcol=refcol, tstcol=tstcol
    )

    futures, written, errors = [], 0, []

    # Submete tarefas — associamos índice 'exp' (1-based)
    with Exeutor(max_workers=max_workers) as ex:
        for i, t in enumerate(tbls):
            exp_idx = i + 1
            futures.append(ex.submit(worker_partial, t, exp_idx))
        
        batch_rows = []
        for fut in as_completed(futures):
            ok, payload = fut.result()

            if ok:
                batch_rows.append(payload)
            else:
                errors.append(payload)
        
        # Write results
        df_batch = pd.DataFrame(batch_rows, columns=cols)

        obj_to_tbl(df_batch, outres)
    
    if errors:
        err_path = os.path.splitext(outres)[0] + '_errors.log'
        with open(err_path, 'w', encoding='utf-8') as eh:
            for e in errors:
                eh.write(str(e) + "\n\n")
    
    return outres


def eval_binarytrain(clsres, rid, refcol, clscol, osmtxt, out):
    """
    N models were tested using the same test records

    We want to know which are the records well classified most of the time
    and otherwise.
    """
    

    db = create_pgdb(fprop(out, 'fn'), overwrite=True)

    tables = lst_ff(clsres, file_format='.xlsx')

    ftbl = 'our_data'
    ires = multixlsx_to_onetable(tables, db, ftbl, cols=[rid, refcol, clscol, osmtxt])
    
    # Export Results
    q = (
        f"SELECT {rid}, {refcol}, "
        "SUM(truerate) AS truerate, "
        "SUM(falserate) AS falserate, "
        f"{osmtxt} "
        "FROM ("
            f"SELECT {rid}, {refcol}, {osmtxt}, "
            "CASE "
                f"WHEN {refcol} = {clscol} "
                "THEN 1 ELSE 0 "
            "END AS truerate, "
            "CASE "
                f"WHEN {refcol} = {clscol} "
                "THEN 0 ELSE 1 "
            "END AS falserate "
            "FROM our_data"
        ") AS foo "
        f"GROUP BY {rid}, {refcol}, {osmtxt}"
    )

    fdf = q_to_obj(db, q)

    fdf['nclass'] = fdf.truerate + fdf.falserate
    fdf['sucrate'] = fdf.truerate / fdf.nclass * 100

    goodrate = fdf[fdf.sucrate > 85]
    doubt = fdf[fdf.sucrate >= 40]

    doubt[refcol] = np.where(
        (doubt.sucrate >= 40) & (doubt.sucrate <= 60),
        1, np.where(
            doubt.sucrate >= 85, 0, -1
        )
    ) 

    doubt = doubt[doubt[refcol] > -1]

    obj_to_tbl(
        [fdf, goodrate, doubt], out,
        sheetsName=['all_records', 'hightruerate', 'uncertainty']
    )

    return out

