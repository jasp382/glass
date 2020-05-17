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
    from glass.oss                   import get_filename
    from glass.cpu.arcg.lyr         import rst_lyr
    from glass.cpu.arcg.lyr         import feat_lyr
    from glass.cpu.to.shp.arcg      import rst_to_pnt
    from glass.cpu.arcg._3D.mng.tin import create_tin
    from glass.cpu.to.rst.arcg      import tin_to_raster
    
    workspace = workspace if workspace else \
        os.path.dirname(outRst)
    
    # Convert Input Raster to a Point Feature Class
    rstLyr = rst_lyr(inRst)
    pntRst = rst_to_pnt(
        rstLyr,
        os.path.join(workspace, get_filename(inRstinRst) + '.shp')
    )
    
    # Create TIN
    pntrstLyr = feat_lyr(  pntRst)
    lmtLyr    = feat_lyr(boundary)
    
    tinInputs = (
        '{bound} <None> Soft_Clip <None>;'
        '{rst_pnt} GRID_CODE Mass_Points <None>'
    )
    
    tinOutput = os.path.join(workspace, 'tin_' + get_filename(inRst))
    
    create_tin(tinOutput, prj, tinInputs)
    
    return tin_to_raster(tinOutput, cellsize, outRst, template=template)

