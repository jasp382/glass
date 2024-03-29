"""
Classify using model in file
"""

if __name__ == "__main__":
    import os
    from glass.rd import tbl_to_obj
    from glass.rst.cls import imgcls_from_mdl

    reffile  = '/mnt/g/autocls_franc/cls_exp.xlsx'
    refsheet = 'mainsheet2'


    mdf = tbl_to_obj(reffile, sheet=refsheet)

    for i, row in mdf.iterrows():
        if not i:
            continue
        
        cvar = tbl_to_obj(reffile, sheet=row.sheet)
    
        imgcls_from_mdl(
            row.trainfile,
            [os.path.join(row.class_folder, f) for f in cvar.classvar.tolist()],
            row.result
        )

