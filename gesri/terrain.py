"""
DEM's in ArcGIS
"""

import arcpy

def countours_to_tin(elevation, elvfield, lmt, prj, output, hydrology=None):
    """
    Create Raster DEM from TIN
    """
    
    import os
    from glass.pys.oss    import fprop
    from gesri.rd.shp     import shp_to_lyr
    from gesri.threed.tin import create_tin
    
    lyr_elev = shp_to_lyr(elevation)
    lyr_lmt  = shp_to_lyr(lmt)

    bname = fprop(lmt, 'fn')
    ename = fprop(elevation, 'fn')
    
    if not hydrology:
        __inputs = (
            "bnd_lyr <None> Soft_Clip <None>; "
            "elev_lyr {fld} Mass_Points <None>"
        ).format(
            bound=os.path.splitext(os.path.basename(lmt))[0],
            alti=os.path.splitext(os.path.basename(elevation))[0],
            fld=str(elvfield)
        )
    
    else:
        lyr_hidro = shp_to_lyr(hydrology)
        
        __inputs = (
            "bnd_lyr <None> Soft_Clip <None>; "
            "elev_lyr {fld} Mass_Points <None>; "
            "{hidro} <None> Hard_Line <None>"
        ).format(
            bound=os.path.splitext(os.path.basename(lmt))[0],
            alti=os.path.splitext(os.path.basename(elevation))[0],
            fld=str(elvfield),
            hidro=os.path.splitext(os.path.basename(hydrology))[0]
        )
    
    if type(prj) == int:
        from gesri.df.prop.prj import get_wkt_esri
        
        prjWkt = get_wkt_esri(prj)
    else:
        prjWkt = prj
    
    create_tin(output, prjWkt, __inputs)
    
    return output


def dem_from_tin(
    countors, elevation_field, boundary_tin, boundary_mdt,
    cellsize, w, output, hidrology=None, __hillshade=None,
    snapRst=None, prj=None):
    """
    Create a Digital Elevation Model based on a TIN
    """
    
    import os
    from glass.pys.oss          import fprop
    from gesri.rd.shp          import shp_to_lyr
    from gesri.dct.torst          import tin_to_raster
    from gesri.df.mng.rst.proc import clip_raster
    
    oprop = fprop(output, ['fn', 'ff'])
    oname, of = oprop['filename'], oprop['fileformat']

    if not os.path.exists(w):
        from glass.pys.oss import create_folder
        create_folder(w, overwrite=None)
    
    # Check Extension
    arcpy.CheckOutExtension("3D")
    # Configure workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = w
    
    prj = os.path.splitext(countors)[0] + '.prj' if not prj else prj
    
    if type(prj) == int:
        from glass.gt.prop.prj import get_prj_web
    
        prj = get_prj_web(prj, os.path.join(
            w, 'prj_{}.prj'.format(str(prj))
        ))
    
    else:
        if not os.path.exists(prj):
            prj = os.path.splitext(boundary_mdt)[0] + '.prj'
            if not os.path.exists(prj):
                proj = os.path.splitext(boundary_tin)[0] + '.prj'
                if not os.path.exists(prj):
                    raise ValueError('On of the inputs must have a prj file')
    
    
    
    # Create TIN
    tin = create_TINdem(countors, elevation_field, boundary_tin, prj,
                       'tin_tmp', hidrology)
    # TIN2Raster
    rst_tin = tin_to_raster(
        tin, cellsize, f'{oname}_extra{of}', snapRst=snapRst
    )
    
    # Clip Raster
    lmt_clip = shp_to_lyr(boundary_mdt)
    dem_clip = clip_raster(rst_tin, lmt_clip, output, snap=snapRst)
    
    # Create Hillshade just for fun
    if __hillshade:
        from gesri.df.spanlst.surf import hillshade
        
        hillshd = hillshade(output, os.path.join(
            os.path.dirname(output), f'{oname}hsd{of}'
        ))


def loop_dem_from_tin(countors_fld, elevField, bound_tin_fld, bound_mdt_fld,
                 cellsize, w, fld_outputs, snapRst=None, prj=None,
                 shpFormat='.shp', rstFormat='.tif'):
    """
    Create a Digital Elevation Model based on a TIN in loop
    
    NOTES:
    * Related countours and boundaries should have the same name in the
    respective folder
    
    * elevField should be the same in all countors_fld
    """
    
    import os
    from glass.pys.oss import lst_ff
    
    # List files
    countours = lst_ff(countors_fld, file_format=shpFormat)
    
    rstFormat = rstFormat if rstFormat[0] == '.' else '.' + rstFormat
    shpFormat = shpFormat if shpFormat[0] == '.' else '.' + shpFormat
    
    for shp in countours:
        shpFilename = os.path.basename(shp)
        
        dem_from_tin(
            shp, elevField,
            os.path.join(bound_tin_fld, shpFilename),
            os.path.join(bound_mdt_fld, shpFilename),
            cellsize,
            w,
            os.path.join(
                fld_outputs,
                os.path.splitext(shpFilename)[0] + rstFormat
            ),
            snapRst=snapRst,
            prj=prj
        )

