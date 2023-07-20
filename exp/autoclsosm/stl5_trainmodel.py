"""
Produce Model file
"""

if __name__ == "__main__":

    import os
    from glass.rd      import tbl_to_obj
    from glass.rst.cls import train_to_mdl

    reffile  = '/mnt/disk1/jasp/expfrancisco/exp_francisco.xlsx'
    refsheet = 'mainsheet'


    mdf = tbl_to_obj(reffile, sheet=refsheet)

    for i, row in mdf.iterrows():
        cvar = tbl_to_obj(reffile, sheet=row.sheet)
    
        train_to_mdl(
            row.traindata,
            [os.path.join(row.train_folder, f) for f in cvar.trainvar.tolist()],
            row.trainfile,
            ntrees=row.ntrees,
            method=row.classifier
        )

