"""
Perigosity models validation
"""


def pseudo_roc(ref, perigo_rst, posval, otbl=None):
    """
    Oliveira et al 2021 validation metrics implementation
    """

    import numpy as np
    import pandas as pd

    from sklearn import metrics

    from glass.rd.rst   import rst_to_array
    from glass.prop.rst import get_nodata
    from glass.wt       import obj_to_tbl

    # Open Reference dataset
    ref_array = rst_to_array(ref)
    ref_nd    = get_nodata(ref)

    # Get frequencies - count number of burned pixels in the reference
    refv, reffreq = np.unique(ref_array, return_counts=True)

    _refv   = refv[refv != ref_nd]
    reffreq = reffreq[refv != ref_nd]

    # Open result to be validated
    prob_array = rst_to_array(perigo_rst)

    prob_nd = round(get_nodata(perigo_rst) * 10000, 0)

    # Get scores frequencies 
    int_array = np.round_(prob_array * 10000, decimals=0)
    int_array = int_array.astype(np.int32)

    vals, freq = np.unique(int_array, return_counts=True)

    _vals = vals[vals != prob_nd]
    freq  = freq[vals != prob_nd]

    # Only Presences
    ref_val = np.where(
        ref_array == posval, int_array,
        -99999
    )

    refvals, reffreq = np.unique(ref_val, return_counts=True)

    _refvals = refvals[refvals != -99999]
    reffreq  = reffreq[refvals != -99999]

    # Validation tables
    freq_a = pd.DataFrame({"vals": _vals, "areafreq" : freq})
    freq_b = pd.DataFrame({"fvals": _refvals, "firefreq" : reffreq})

    ftbl = freq_a.merge(freq_b, how='left', left_on='vals', right_on='fvals')

    ftbl.drop('fvals', axis=1, inplace=True)

    ftbl['firefreq'] = np.where(
        ftbl.firefreq.isna(), 0,
        ftbl.firefreq
    )

    ftbl.sort_values(by='vals', ascending=False, inplace=True)
    ftbl.reset_index(inplace=True)

    ftbl["cumarea"] = ftbl.areafreq.cumsum()
    ftbl["cumfire"] = ftbl.firefreq.cumsum()

    areat = ftbl.areafreq.sum()
    firet = ftbl.firefreq.sum()

    ftbl["tarearatio"] = ftbl.cumarea / float(areat)
    ftbl["tfireration"] = ftbl.cumfire / float(firet)

    # Calculate pseudo AUC
    auxtbl = ftbl.copy(deep=True)

    dc = [c for c in ftbl.columns.values if c != 'tarearatio' and c != 'tfireration']
    auxtbl.drop(dc, axis=1, inplace=True)
    auxtbl.rename(columns={'tarearatio' : 'aratio', 'tfireration' : 'fratio'}, inplace=True)

    ftbl['lidx'] = ftbl.index
    auxtbl['ridx'] = auxtbl.index + 1

    ftbl = ftbl.merge(auxtbl, how='left', left_on='lidx', right_on='ridx')

    ftbl['aratio'] = np.where(
        ftbl.aratio.isna(), 0,
        ftbl.aratio
    )

    ftbl['fratio'] = np.where(
        ~ftbl.fratio.isna(),
        ftbl.fratio, 0
    )

    ftbl["auc_a"] = ftbl['tarearatio'] - ftbl.aratio
    ftbl["auc_b"] = (ftbl['tfireration'] + ftbl.fratio) /2.0

    ftbl["auc_c"] = ftbl.auc_b * ftbl.auc_a

    auc = ftbl.auc_c.sum()

    realauc = metrics.auc(ftbl["tarearatio"], ftbl["tfireration"])

    if otbl:

        obj_to_tbl(ftbl, otbl)

        return otbl, realauc, auc
    
    else:
        return ftbl, realauc, auc

