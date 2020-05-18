"""
Shape difference to matrices
"""

if __name__ == '__main__':
    from gasp.gt.gop.ovlay import shp_diff_fm_ref

    ref  = '/home/jasp/mrgis/landsense_eval/cos18_l1_v3.shp'
    rcol = 'cls_i'

    compare = {
        '/home/jasp/mrgis/landsense_eval/res_lsb_f2.tif' : None,
        '/home/jasp/mrgis/landsense_eval/rst_train_f2.tif' : None,
        '/home/jasp/mrgis/landsense_eval/train_rst.tif' : None,
        '/home/jasp/mrgis/landsense_eval/train_f0.shp' : 'cls_i'
    }

    out = '/home/jasp/mrgis/landsense_eval/results'

    refrst = '/home/jasp/mrgis/landsense_eval/rst_lisboa.tif'

    shp_diff_fm_ref(
        ref, rcol, compare, out, refrst
    )

