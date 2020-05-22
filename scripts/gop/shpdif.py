"""
Shape difference to matrices
"""

if __name__ == '__main__':
    from glass.geo.gt.gop.ovlay import shp_diff_fm_ref

    ref  = '/home/jasp/mrgis/clsimg/refdata/lsb_cos18_l1.shp'
    rcol = 'cls_i'

    compare = {
        '/home/jasp/mrgis/clsimg/lsb_f0_res1.tif' : None,
        '/home/jasp/mrgis/clsimg/lsb_f1_res1.tif' : None,
        '/home/jasp/mrgis/clsimg/lsb_f2_res1.tif' : None,
        '/home/jasp/mrgis/clsimg/lsb_f0_res2.tif' : None,
        '/home/jasp/mrgis/clsimg/lsb_f1_res2.tif' : None,
        '/home/jasp/mrgis/clsimg/lsb_f2_res2.tif' : None,
    }

    out = '/home/jasp/mrgis/clsimg/eval_lsb_res12'

    refrst = '/home/jasp/mrgis/clsimg/refdata/rst_lisboa.tif'

    shp_diff_fm_ref(
        ref, rcol, compare, out, refrst
    )

