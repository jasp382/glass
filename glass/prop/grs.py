"""
GRASS GIS Session properties
"""


def list_raster():
    """
    GRASS g.list

    List all rasters in the workspace
    """

    import subprocess

    from grass.pygrass.modules import Module

    listcmd = Module(
        "g.list",  type='raster',
        run_=False, quiet=True, stdout_=subprocess.PIPE
    )

    listcmd()

    output = listcmd.outputs.stdout

    return output[:-2].split('\n')

