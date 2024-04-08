"""
OSM Classification tools
"""

import joblib

from glass.rd import tbl_to_obj
from glass.wt import obj_to_tbl


def osmtext_to_model(txt_tbl, sheet, refcls, txtcol, omdl, ovec=None, ntrees=1000, smax=None, cweight=None):
    """
    Create Model based on OSM text
    """

    from sklearn.ensemble import RandomForestClassifier

    from glass.cls.txt import txt_to_num_representation

    txtdf = tbl_to_obj(txt_tbl, sheet=sheet)

    feat, tvect = txt_to_num_representation(
        txtdf, txtcol, 'english',
        returnTfiDf=True, osm_use_case=True
    )

    rf = RandomForestClassifier(
        n_estimators=ntrees, random_state=0,
        n_jobs=-1,
        bootstrap=True,
        max_samples=smax,
        class_weight=cweight
    )

    txtdf[refcls] = txtdf[refcls].astype(int)

    rf.fit(feat, txtdf[refcls])

    # Save model
    joblib.dump(rf, omdl)

    if ovec:
        joblib.dump(tvect, ovec)

    return omdl, ovec


def osmtext_class(tbl, txtcol, model, tvec, out, sheet=None, inputsAsFile=True, outcol='class_res'):
    """
    OSM Text classification
    """

    from joblib import load

    if inputsAsFile:
        cdf = tbl_to_obj(tbl, sheet=sheet)

        mdl, tv = load(model), load(tvec)
    
    else:
        cdf,  mdl, tv = tbl, model, tvec

    feat = tv.transform(cdf[txtcol])

    ypred = mdl.predict(feat)
    yprob = mdl.predict_proba(feat)
    yprob = yprob[:, 1]

    cdf.loc[:, outcol] = ypred
    cdf.loc[:, f'{outcol}_prob'] = yprob

    obj_to_tbl(cdf, out)

    return out

