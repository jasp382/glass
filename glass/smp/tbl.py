"""
Create samples from table
"""

import os
import numpy as np
import pandas as pd


from glass.rd         import tbl_to_obj
from glass.dtt.mge.pd import merge_df
from glass.wt         import obj_to_tbl


def binref_to_trainval(refdata, refcol, posval, negval, out_train, out_val, sheet=None):
    """
    Binary Reference table to train and validation tables
    Split 60/40
    """
    
    df = tbl_to_obj(refdata, sheet=sheet)

    # Split positives and negatives
    pdf = df[df[refcol] == posval]
    ndf = df[df[refcol] == negval]

    pdf.reset_index(inplace=True)
    pdf.drop(['index'], axis=1, inplace=True)
    pdf['idx'] = pdf.index

    ndf.reset_index(inplace=True)
    ndf["idx"] = ndf.index

    ndf.drop(['index'], axis=1, inplace=True)

    # Split into train and test
    train, test = [], []
    for _df in [pdf, ndf]:
        nfeat = int(round(60 * _df.shape[0] / 100))

        rd = np.random.choice(_df.idx, nfeat, replace=False)

        tdf = _df[_df.idx.isin(rd)]
        vdf = _df[~_df.idx.isin(rd)]

        train.append(tdf)
        test.append(vdf)
    
    traindf = merge_df(train)
    testdf_ = merge_df(test)

    obj_to_tbl(traindf, out_train, sheetsName=sheet)
    obj_to_tbl(testdf_, out_val, sheetsName=sheet)

    return out_train, out_val



def binref_to_trainval_samples(refdata, refcol, posval, negval, trainfolder, tstfolder, sheet=None, nsamples=100, trainperc=70):
    """
    Binary Reference table to train and validation tables

    Create N train/test tables
    N = nsamples
    """

    from glass.pys.oss import mkdir

    if not os.path.exists(trainfolder):
        mkdir(trainfolder)

    if not os.path.exists(tstfolder):
        mkdir(tstfolder)
    
    df = tbl_to_obj(refdata, sheet=sheet)

    # Create DF for positives, other for negatives
    pdf = df[df[refcol] == posval]
    ndf = df[df[refcol] == negval]

    nneg = pdf.shape[0] * 3
    if nneg > ndf.shape[0]:
        nneg = ndf.shape[0]
    
    tsample = pdf.shape[0] + nneg

    pdf.reset_index(inplace=True)
    pdf.drop(['index'], axis=1, inplace=True)
    pdf['idx'] = pdf.index

    ndf.reset_index(inplace=True)
    ndf["idx"] = ndf.index

    ndf.drop(['index'], axis=1, inplace=True)

    train_dfs, val_dfs = [], []

    for i in range(nsamples):
        rnd = np.random.choice(ndf.idx, nneg, replace=False)

        negsample = ndf[ndf.idx.isin(rnd)]

        # Split into train and test
        trval = {"train" : [], "val" : []}

        for _df in [pdf, negsample]:
            nfeat = int(round(int(trainperc) * _df.shape[0] / 100.0))

            rd = np.random.choice(_df.idx, nfeat, replace=False)

            train = _df[_df.idx.isin(rd)]
            val   = _df[~_df.idx.isin(rd)]

            trval["train"].append(train)
            trval["val"].append(val)
        
        traindf = merge_df(trval["train"])
        valdf   = merge_df(trval["val"])

        train_dfs.append(traindf)
        val_dfs.append(valdf)
    
    train_xls, tst_xls = [], []
    for i in range(len(train_dfs)):
        otrain = obj_to_tbl(train_dfs[i], os.path.join(trainfolder, f'train_{i}.xlsx'), sheetsName=sheet)
        otest  = obj_to_tbl(val_dfs[i], os.path.join(tstfolder, f'val_{i}.xlsx'), sheetsName=sheet)

        train_xls.append(otrain)
        tst_xls.append(otest)
    
    return train_xls, tst_xls


def ref_to_trainval_twice(reftbl, refcol, train_dim, subdim, trainfolder, tst_table, nmodels=200, refsheet=None, filter_cols=None):
    """
    Split reference into Train and Test 70/30

    In a second moment, split Train into N train sub-samples
    Idea is to test which records should be part of the train 
    """

    from glass.pys.oss import mkdir

    if not os.path.exists(trainfolder):
        mkdir(trainfolder)
    
    df = tbl_to_obj(reftbl, sheet=refsheet, fields=filter_cols+[refcol])

    df[refcol] = df[refcol].astype(int)

    # Get frequencies
    freq = pd.DataFrame({
        'freq_cls' : df.groupby([refcol])[refcol].agg('count')
    }).reset_index()

    freq['ntrain']  = freq.freq_cls * train_dim / 100
    freq['percent'] = freq.freq_cls / freq.freq_cls.sum() * 100
    freq['ntrain']  = freq.ntrain.round()
    freq['ntrain']  = freq['ntrain'].astype(int)
    if subdim <= 1:
        freq["subsample"] = freq.ntrain * subdim
    else:
        freq["subsample"] = subdim
    freq["subsample"] = freq["subsample"].astype(int)

    # Split reference data
    # 60% for training
    # 40% for validation
    trains, tests = [], []
    trains_samples = [[] for o in range(nmodels)]
    for i, row in freq.iterrows():
        vdf = df[df[refcol] == row[refcol]]

        vdf.reset_index(inplace=True)
        vdf.drop(['index'], axis=1, inplace=True)
        
        vdf['idx'] = vdf.index

        rd = np.random.choice(vdf.idx, int(round(row.ntrain)), replace=False)

        train = vdf[vdf.idx.isin(rd)]
        val   = vdf[~vdf.idx.isin(rd)]

        train.reset_index(inplace=True)
        train.drop(["idx", "index"], inplace=True, axis=1)
        val.drop(["idx"], inplace=True, axis=1)

        trains.append(train)
        tests.append(val)

        # Train subsampling
        train['idx'] = train.index
        for e in range(nmodels):
            if row.subsample >= train.shape[0] * 0.70:
                nsubsample = int(round(train.shape[0] * 0.7))
            
            else:
                nsubsample = int(round(row.subsample))
            _r = np.random.choice(train.idx, nsubsample, replace=False)

            subdf = train[train.idx.isin(_r)]

            subdf.drop(['idx'], axis=1, inplace=True)

            trains_samples[e].append(subdf)
    
    # Get main train/test dataset
    ptraindf = merge_df(trains)
    valdf    = merge_df(tests)

    obj_to_tbl([valdf, ptraindf, freq], tst_table, sheetsName=[refsheet, 'pseudo_train', 'freq'])

    # Save subsamples
    trainsubsamples = []
    for i, ss in enumerate(trains_samples):
        ttt = merge_df(ss)

        res = obj_to_tbl(ttt, os.path.join(trainfolder, f'train_{str(i)}.xlsx'), sheetsName=refsheet)

        trainsubsamples.append(res)

    return trainsubsamples, tst_table

