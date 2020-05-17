"""
Compare CAE with data sources
"""

if __name__ == "__main__":
    from glass.ete.cae import caevs_multiproc

    caefolder = '/home/jasp/mystuff/dgt_caeosm/refdata_dgt/caeparts'
    polyfolder = '/home/jasp/mystuff/dgt_caeosm/osmdata/osmshp_v3'
    reffolder  = '/home/jasp/mystuff/dgt_caeosm/lmt/refparts'
    cls = "Id"
    source = "osm"
    ofolder = '/home/jasp/mystuff/dgt_caeosm/caevs_results/res_osm_v3'

    caevs_multiproc(
        reffolder, caefolder, polyfolder, cls, source,
        ofolder
    )

