"""
Variables normalization
"""


def norm_in_fc(shp, idcol, rules, oscore, oshp):
    """
    Normalize variables in Feature Class

    rules sample:
    rules = {
        'file'    : '/mnt/e/bestevus/regras_normalizacao.xlsx',
        'sheet'   : 'regras_v4',
        'shpcol'  : 'coluna',
        'method'  : 'method',
        'goaldir' : 'goaldirection'
    }
    """

    from glass.rd     import tbl_to_obj
    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp

    df_r = tbl_to_obj(rules['file'], sheet=rules['sheet'])

    shpdf = shp_to_obj(shp)

    resdf = shpdf[[idcol, 'geometry']]

    resdf[oscore] = 0

    for i, r in df_r.iterrows():
        col  = r[rules['shpcol']]
        meth = r[rules['method']]
        gdir = r[rules['goaldir']]

        if meth == 'range' and gdir == 'max':
            resdf[col] = (shpdf[col] - shpdf[col].min()) / (shpdf[col].max() - shpdf[col].min())

        elif meth == 'range' and gdir == 'min':
            resdf[col] = (shpdf[col].max() - shpdf[col]) / (shpdf[col].max() - shpdf[col].min())

        elif meth == 'max' and gdir == 'max':
            resdf[col] = shpdf[col] / shpdf[col].max()

        else:
            resdf[col] = 1 - (shpdf[col] / shpdf[col].max())

        resdf[oscore] = resdf[oscore] + resdf[col]
    
    df_to_shp(resdf, oshp)

    return oshp

