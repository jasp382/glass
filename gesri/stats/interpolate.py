"""
More complex Interpolation methods for ArcGIS
"""

import arcpy

def TIN_nodata_interpolation(inRst, boundary, prj, cellsize, outRst,
                             workspace=None, template=None):
    """
    Preenche os valores NoData de uma imagem raster usando um TIN
    """
    
    import os
    from glass.pys.oss                   import fprop
    from gesri.rd.rst         import rst_to_lyr
    from gesri.rd.shp         import shp_to_lyr
    from glass.cpu.to.shp.arcg      import rst_to_pnt
    from glass.cpu.arcg._3D.mng.tin import create_tin
    from glass.cpu.to.rst.arcg      import tin_to_raster
    
    workspace = workspace if workspace else \
        os.path.dirname(outRst)

    rstname = fprop(inRst, 'fn')
    
    # Convert Input Raster to a Point Feature Class
    rstLyr = rst_to_lyr(inRst)
    pntRst = rst_to_pnt(rstLyr, os.path.join(
        workspace, f" {rstname}.shp"))
    
    # Create TIN
    pntrstLyr = shp_to_lyr(  pntRst)
    lmtLyr    = shp_to_lyr(boundary)
    
    tinInputs = (
        '{bound} <None> Soft_Clip <None>;'
        '{rst_pnt} GRID_CODE Mass_Points <None>'
    )
    
    tinOutput = os.path.join(workspace, f'tin_{rstname}')
    
    create_tin(tinOutput, prj, tinInputs)
    
    return tin_to_raster(tinOutput, cellsize, outRst, template=template)

