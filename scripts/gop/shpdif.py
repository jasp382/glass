"""
Shape difference to matrices
"""

if __name__ == '__main__':
    from glass.geo.gt.gop.ovlay import shp_diff_fm_ref

    ref  = '/home/jasp/mrgis/pnse_eval/pnse_cos18_l1.shp'
    rcol = 'cls_i'

    compare = {
        #'/home/jasp/mrgis/landsense_eval/res_lsb_f1.tif'   : None,
        #'/home/jasp/mrgis/landsense_eval/res_lsb_f2.tif'   : None,
        #'/home/jasp/mrgis/landsense_eval/train_f0.shp'     : 'cls_i',
        #'/home/jasp/mrgis/landsense_eval/train_rst.tif'    : None,
        #'/home/jasp/mrgis/landsense_eval/rst_train_f2.tif' : None
        '/home/jasp/mrgis/pnse_eval/train_f0.shp' : 'lulc',
        '/home/jasp/mrgis/pnse_eval/train_filter1.tif' : None,
        '/home/jasp/mrgis/pnse_eval/train_f2.tif' : None,
    }

    out = '/home/jasp/mrgis/pnse_eval/results'

    refrst = '/home/jasp/mrgis/pnse_eval/rst_pnse.tif'

    shp_diff_fm_ref(
        ref, rcol, compare, out, refrst
    )

