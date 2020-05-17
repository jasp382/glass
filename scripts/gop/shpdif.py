"""
Shape difference to matrices
"""

if __name__ == '__main__':
    from glass.geo.gt.gop.ovlay import shp_diff_fm_ref

    params = [
        {
            'ref'  : '/home/jasp/mrgis/eval_lsb/lsb_cos18_l1.shp',
            'rcol' : 'cls_i',
            'compare' : {
                '/home/jasp/mrgis/eval_lsb/lsb_f0_500k_4x3_05kt_v2.tif' : None,
                '/home/jasp/mrgis/eval_lsb/lsb_f1_500k_4x3_05kt_v2.tif' : None,
                '/home/jasp/mrgis/eval_lsb/lsb_f2_500k_4x3_05kt_v2.tif' : None,
            },
            'out'    : '/home/jasp/mrgis/eval_lsb/lsb_cosvscls_v2',
            'refrst' : '/home/jasp/mrgis/eval_lsb/rst_lisboa.tif'
        }
    ]

    for d in params:
        shp_diff_fm_ref(
            d['ref'], d['rcol'], d['compare'], d['out'], d['refrst']
        )

