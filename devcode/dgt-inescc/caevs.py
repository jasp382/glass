"""
Compare CAE with data sources
"""

if __name__ == "__main__":
    from glass.ete.cae import caevs_multiproc

    caefolder = '/home/jasp/mystuff/dgt/caeparts/'
    polyfolder = '/home/jasp/mystuff/dgt/builtup/'
    reffolder  = '/home/jasp/mystuff/dgt/refparts/'
    cls = "gridcode"
    source = "bup"
    ofolder = '/home/jasp/mystuff/dgt/rbuiltup/'

    caevs_multiproc(
        reffolder, caefolder, polyfolder, cls, source,
        ofolder
    )

