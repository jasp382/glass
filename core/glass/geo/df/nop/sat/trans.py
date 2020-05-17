"""
Transform Satellite Imagery
"""

def rgb_to_ihs(bred, bgreen, bblue, outbase):
    """
    RGB to IHS
    """
    
    from grass.pygrass.modules import Module
    
    HUE        = "{}_hue".format(outbase)
    INTENSITY  = "{}_intensity".format(outbase)
    SATURATION = "{}_saturation".format(outbase)
    
    t = Module(
        "i.rgb.his", red=bred, green=bgreen, blue=bblue,
        hue=HUE, intensity=INTENSITY, saturation=SATURATION,
        overwrite=True, run_=False
    )
    
    t()
    
    return INTENSITY, HUE, SATURATION


def ihs_to_rgb(inte, hue, sat, outbase):
    """
    IHS to RGB
    """
    
    from grass.pygrass.modules import Module
    
    RED   = "{}_red".format(outbase)
    GREEN = "{}_green".format(outbase)
    BLUE  = "{}_blue".format(outbase)
    
    t = Module(
        'i.his.rgb', hue=hue, intensity=inte, saturation=sat,
        red=RED, green=GREEN, blue=BLUE,
        overwrite=True, run_=False
    )

def ihs_pansharpen(red, green, blue, pancromatic, out):
    """
    IHS_Pansharpen
    """
    
    from grass.pygrass.modules import Module
    
    t = Module(
        "i.pansharpen", red=red, green=green, blue=blue,
        pan=pancromatic, output=out, method="ihs"
    )
    
    t()
    
    return out + "_red", out + "_green", out + "_blue"
