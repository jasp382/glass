"""
Shape difference to matrices
"""

if __name__ == '__main__':
    from glass.geo.gt.gop.ovlay import shp_diff_fm_ref

    ref  = '/home/osmtolulc/mrgis/clsimg/lsb_cos18_l1.shp'
    rcol = 'cls_i'

    compare = {
        '/home/osmtolulc/mrgis/clsimg/rf_results/lsb_f0_500k_4x3_05kt.tif' : None,
        '/home/osmtolulc/mrgis/clsimg/rf_results/lsb_f1_500k_4x3_05kt.tif' : None,
        '/home/osmtolulc/mrgis/clsimg/rf_results/lsb_f2_500k_4x3_05kt.tif' : None
    }

    out = '/home/osmtolulc/mrgis/clsimg/eval_lsb_4x3_05'

    refrst = '/home/osmtolulc/mrgis/clsimg/rst_lisboa.tif'

    shp_diff_fm_ref(
        ref, rcol, compare, out, refrst
    )

