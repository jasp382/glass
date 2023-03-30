"""
Run Informative Value Method in different Software
"""


def infovalue(landslides, variables, iv_rst):
    """
    Informative Value using GDAL Library
    """
    
    import os
    import math
    import numpy
    from glass.rd.rst    import rst_to_array
    from glass.rd       import tbl_to_obj
    from glass.prop.feat import get_gtype
    from glass.prop.rst  import rst_shape
    from glass.prop.rst  import count_cells
    from glass.prop.rst  import get_cellsize
    from glass.prop.rst  import frequencies
    from glass.pys.oss     import mkdir
    from glass.wt.rst    import obj_to_rst
    
    # Create Workspace for temporary files
    workspace = mkdir(os.path.join(
        os.path.dirname(landslides), 'tmp')
    )
    
    # Get Variables Raster Shape and see if there is any difference
    varShapes = rst_shape(variables)
    for i in range(1, len(variables)):
        if varShapes[variables[i-1]] != varShapes[variables[i]]:
            raise ValueError((
                'All rasters must have the same dimension! '
                'Raster {} and Raster {} have not the same shape!'
            ).format(variables[i-1], variables[i]))
    
    # See if landslides are raster or not
    # Try to open as raster
    try:
        land_rst = rst_to_array(landslides)
        lrows, lcols = land_rst.shape
        
        if [lrows, lcols] != varShapes[variables[0]]:
            raise ValueError((
                "Raster with Landslides ({}) has to have the same "
                "dimension that Raster Variables"
            ).format(landslides))
    
    except:
        # Landslides are not Raster
        # Open as Feature Class
        # See if is Point or Polygon
        land_df  = tbl_to_obj(landslides)
        geomType = get_gtype(land_df, geomCol="geometry", gisApi='pandas')
        
        if geomType == 'Polygon' or geomType == 'MultiPolygon':
            # it will be converted to raster bellow
            land_poly = landslides
        
        elif geomType == 'Point' or geomType == 'MultiPoint':
            # Do a Buffer
            from glass.gp.prox.bfing.obj import geodf_buffer_to_shp
            
            land_poly = geodf_buffer_to_shp(land_df, 100, os.path.join(
                workspace, 'landslides_buffer.shp'
            ))
        
        # Convert To Raster
        from glass.dtr.torst import shp_to_rst
        
        land_raster = shp_to_rst(
            land_poly, None, get_cellsize(variables[0], gisApi='gdal'), -9999,
            os.path.join(workspace, 'landslides_rst.tif'),
            rst_template=variables[0], api='gdal'
        )
        
        land_rst = rst_to_array(land_raster)
    
    # Get Number of cells of each raster and number of cells
    # with landslides
    landsldCells = frequencies(land_raster)[1]
    totalCells   = count_cells(variables[0])
    
    # Get number of cells by classe in variable
    freqVar = { r : frequencies(r) for r in variables }
    
    for rst in freqVar:
        for cls in freqVar[rst]:
            if cls == 0:
                freqVar[rst][-1] = freqVar[rst][cls]
                del freqVar[rst][cls]
            
            else:
                continue
    
    # Get cell number with landslides by class
    varArray = { r : rst_to_array(r) for r in variables }
    
    for r in varArray:
        numpy.place(varArray[r], varArray[r]==0, -1)
    
    landArray  = { r : land_rst * varArray[r] for r in varArray }
    freqLndVar = { r : frequencies(landArray[r]) for r in landArray }
    
    # Estimate VI for each class on every variable
    vi = {}
    for var in freqVar:
        vi[var] = {}
        for cls in freqVar[var]:
            if cls in freqLndVar[var]:
                vi[var][cls] = math.log10(
                    (float(freqLndVar[var][cls]) / freqVar[var][cls]) / (
                        float(landsldCells) / totalCells)
                )
            
            else:
                vi[var][cls] = 9999
    
    # Replace Classes without VI, from 9999 to minimum VI
    vis = []
    for d in vi.values():
        vis += d.values()
    
    min_vi = min(vis)
    
    for r in vi:
        for cls in vi[r]:
            if vi[r][cls] == 9999:
                vi[r][cls] = min_vi
            else:
                continue
    
    # Replace cls by vi in rst_arrays
    resultArrays = {v : numpy.zeros(varArray[v].shape) for v in varArray}
    for v in varArray:
        numpy.place(resultArrays[v], resultArrays[v] == 0, -128)
    
    for v in varArray:
        for cls in vi[v]:
            numpy.place(resultArrays[v], varArray[v]==cls, vi[v][cls])
    
    # Sum all arrays and save the result as raster
    vi_rst = resultArrays[variables[0]] + resultArrays[variables[1]]
    for v in range(2, len(variables)):
        vi_rst = vi_rst + resultArrays[variables[v]]
    
    numpy.place(vi_rst, vi_rst == len(variables) * -128, -128)
    
    result = obj_to_rst(vi_rst, iv_rst, variables[i], noData=-128)
    
    return iv_rst


def grs_infovalue(movs, _var, refrst, out):
    """
    Informative Value estimation using GRASS GIS
    """

    import os
    import math as m
    from glass.dtr.ext.torst import rstext_to_rst
    from glass.prop          import is_rst
    from glass.prop.rst      import rst_shape, frequencies
    from glass.wenv.grs      import run_grass
    from glass.pys.oss       import lst_ff, fprop

    # Get reference raster
    ws = os.path.dirname(out)
    
    refrst = rstext_to_rst(refrst, os.path.join(ws, 'refrst.tif'))

    # List raster files
    rstvar = lst_ff(_var, file_format='tif')

    # Get Reference raster shape (number of rows and columns)
    refshape = rst_shape(refrst)

    # Get Variables Rasters Shape and see if there is any difference
    # comparing with reference
    varshp = rst_shape(rstvar)

    for r in varshp:
        if varshp[r] != refshape:
            raise ValueError((
                f'All rasters must have the same dimension! '
                f'{r} have different shape when compared with refrst!'
            ))
    
    # Start GRASS GIS Session
    # Get name for GRASS GIS location
    loc = fprop(movs, 'fn', forceLower=True)[:7] + '_loc'

    # Create GRASS GIS location
    gbase = run_grass(ws, location=loc, srs=refrst)

    # Start GRASS GIS Session
    import grass.script.setup as gsetup

    gsetup.init(gbase, ws, loc, 'PERMANENT')

    # Import GRASS GIS modules
    from glass.dtr.torst import grsshp_to_grsrst
    from glass.it.shp   import shp_to_grs
    from glass.it.rst   import rst_to_grs, grs_to_rst
    from glass.rst.alg  import rstcalc
    from glass.rst.rcls import category_rules, rcls_rst

    # Check if movs are raster
    isrst = is_rst(movs)

    if isrst:
        movrst = rst_to_grs(movs, fprop(movs, 'fn', forceLower=True))

    else:
        movshp = shp_to_grs(movs, fprop(movs, 'fn', forceLower=True), asCMD=True)
    
        # To raster
        movrst = grsshp_to_grsrst(movshp, 1, f'rst_{movshp}', cmd=True)
    
    # Add rasters to GRASS GIS
    grsvar = [rst_to_grs(r, fprop(r, 'fn', forceLower=True)) for r in rstvar]

    # Get raster representing areas with values in all rasters
    gref = rst_to_grs(refrst, 'refrst')

    i = 1
    for r in grsvar:
        gref = rstcalc(f"int({r} * {gref})", f"refrst_{str(i)}", api='grass')

        i += 1
    
    # Ensure that we have only cells with data in all rasters
    refrules = category_rules({0 : 1}, os.path.join(ws, loc, 'refrules.txt'))

    gref = rcls_rst(gref, refrules, f'rcls_{gref}', api="pygrass")

    grsvar = [rstcalc(f"{r} * {gref}", f"{r}_san", api='grass') for r in grsvar]

    # Export rasters to get frequencies
    filevar = {r : grs_to_rst(r, os.path.join(
        ws, loc, f"{r}.tif"
    ), as_cmd=True) for r in grsvar}

    # Get raster frequencies
    # Negative nodata values are not allowed
    rstfreq = {r : frequencies(filevar[r]) for r in filevar}

    # Count total cells
    i = 0
    for r in rstfreq:
        if not i:
            totalcells = 0
            for v in rstfreq[r]:
                totalcells += rstfreq[r][v]
        
            i += 1
    
        else:
            __totalcells = 0
            for v in rstfreq[r]:
                __totalcells += rstfreq[r][v]
        
            if __totalcells != totalcells:
                raise ValueError(f'{r} has a different number of cells with data')
    
    # Intersect landslides raster with var rasters
    varwithmov = [rstcalc(f"{movrst} * {r}", f"mov_{r}", api='grass') for r in grsvar]

    # Export rasters to get frequencies
    filemov = {grsvar[i] : grs_to_rst(varwithmov[i], os.path.join(
        ws, loc, f"{varwithmov[i]}.tif"
    ), as_cmd=True) for i in range(len(varwithmov))}

    # Get raster frequencies
    rstmovfreq = {r : frequencies(filemov[r]) for r in filemov}

    # Count total cells with landslides
    i = 0
    for r in rstmovfreq:
        if not i:
            totalmov = 0
            for v in rstmovfreq[r]:
                totalmov += rstmovfreq[r][v]
        
            i += 1
    
        else:
            __totalmov = 0
            for v in rstmovfreq[r]:
                __totalmov += rstmovfreq[r][v]
        
            if __totalmov != totalmov:
                raise ValueError(f'{r} has a different number of cells with data')

    # Estimate VI for each class of every variable
    vi = {}

    denom = totalmov / totalcells
    for r in rstfreq:
        vi[r] = {}
        for cls in rstfreq[r]:
            if cls in rstmovfreq[r]:
                vi[r][cls] = m.log10(
                    (rstmovfreq[r][cls] / rstfreq[r][cls]) / denom
                )
        
            else:
                vi[r][cls] = 9999
    
    # Replace Classes without VI, from 9999 to minimum VI
    vis = []
    for d in vi.values():
        vis += d.values()
    
    min_vi = int(round(min(vis), 4) * 10000)

    for r in vi:
        for cls in vi[r]:
            if vi[r][cls] == 9999:
                vi[r][cls] = min_vi
            else:
                vi[r][cls] = int(round(vi[r][cls], 4) * 10000)
    
    # Reclassify
    vivar = []
    for r in grsvar:
        rules = category_rules(
            vi[r], os.path.join(ws, loc, f'vi_{r}.txt')
        )

        virst = rcls_rst(r, rules, f'vi_{r}', api="pygrass")
    
        vivar.append(virst)

    # Integer to float
    virst = [rstcalc(
        f"{r} / 10000.0", f"{r}_f", api='grass'
    ) for r in vivar]

    # Sum results
    virstfinal = rstcalc(" + ".join(virst), fprop(out, 'fn'), api='grass')

    fffinal = grs_to_rst(virstfinal, out)

    return out

