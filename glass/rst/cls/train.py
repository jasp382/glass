"""
Train Models
"""

import joblib
import xarray as xr

import numpy as np

def extract_feat_values(row, cube):
    featval = cube.sel(
        x=row.geometry.x, y=row.geometry.y,
        method="nearest"
    ).values

    return featval

def model_from_pointsample(featcube, points, refcol, outmdl,
                           ntrees=1000, mxsamples=None, sample_dim=100000, pntlyr=None):
    """
    Train a model from a cube and a point sample
    """

    from sklearn.ensemble     import RandomForestClassifier

    from glass.rd.shp import shp_to_obj

    sample_df = shp_to_obj(points, lyr=pntlyr)

    data_cube = xr.open_zarr(featcube)

    sample_df["featval"] = sample_df.apply(lambda row: extract_feat_values(row, data_cube), axis=1)

    X = np.vstack(sample_df["featval"].values)

    Y = sample_df[refcol].values

    # Train model
    clf = RandomForestClassifier(
        n_estimators=ntrees, random_state=42, n_jobs=-1,
        max_samples=mxsamples
    )

    clf.fit(X, Y)

    joblib.dump(clf, outmdl)

    return outmdl

