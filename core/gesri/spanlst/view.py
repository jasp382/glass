# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Visibility things
"""


def generalize_obs_points(rst, ref_cellsize, output, workspace=None):
    """
    We have one raster, each pixel is an observer point.
    If we have a raster with many pixels, viewshed will not run in a short time
    period. As result, we have to reduce the number of observer points.
    This script accomplish the above using a fishnet based approach
    """
    
    import os
    from glass.oss                 import get_filename
    from glass.oss.ops             import create_folder
    from glass.cpu.arcg.anls.ovlay import erase
    from glass.prop.rst            import get_cellsize
    from glass.cpu.arcg.mng.feat   import feat_to_pnt
    from glass.cpu.arcg.mng.sample import fishnet
    from glass.to.shp              import rst_to_polyg
    
    # 0 - Check cellsize, raster cellsize should be lower than refCellsize
    CELLSIZE = get_cellsize(rst, xy=True, bnd=None, gisApi='arcpy')
    
    if CELLSIZE >= ref_cellsize:
        raise ValueError((
            "{} cellsize is not lower than ref_cellsize"
        ).format(rst))
    
    wTmp = workspace if workspace else create_folder(
        os.path.join(os.path.dirname(output), 'tmp'), overwrite=True
    )
    
    BASENAME = get_filename(rst)
    
    # Change cellsize to REF_CELLSIZE
    # 1) Create fishnet with REF_CELLSIZE
    fishNet = fishnet(
        os.path.join(wTmp, "fish_{}.shp".format(BASENAME)),
        rst, cellWidth=ref_cellsize, cellHeight=ref_cellsize   
    )
    
    # 2) Erase areas with NoData values
    # - Raster to shp
    cls_intPolygon = rst_to_polyg(
        rst, os.path.join(wTmp, 'clsint_{}.shp'.format(BASENAME)),
        gisApi='arcpy'
    )
    
    # - Erase areas of the fishnet that agrees with nodata values in the raster
    tmpErase = erase(
        fishNet, cls_intPolygon,
        os.path.join(wTmp, 'nozones_{}.shp'.format(BASENAME))
    ); trueErase = erase(
        fishNet, tmpErase,
        os.path.join(wTmp, 'fishint_{}.shp'.format(BASENAME))
    )
    
    # 3) Convert erased fishnet to points
    genObs = feat_to_pnt(trueErase, output, pnt_position="INSIDE")
    
    return genObs


def generalize_obs_points_forFolder(FolderRst, refCell, outFolder):
    """
    Loop for generalize_obs_points
    """
    
    import arcpy
    import os
    from glass.oss      import get_filename
    from glass.oss.ops  import create_folder
    from glass.prop.rst import rst_distinct
    
    arcpy.env.workspace = FolderRst
    
    rasters = arcpy.ListRasters()
    
    wTmp = create_folder(os.path.join(outFolder, 'tmp'))
    
    for r in rasters:
        # Check if raster has data
        val = rst_distinct(r, gisApi='arcpy')
        if not len(val):
            continue
        
        # Generate observer points
        generalize_obs_points(r, refCell, os.path.join(
            outFolder, "{}.shp".format(get_filename(r))
        ), workspace=wTmp)
    
    return outFolder


def generate_obs_points_for_large_viewshed(INTEREST_RASTER, DEM, REF_CELLS,
                                           ID_CELLS, OUT_FOLDER, SNAP_RASTER,
                                           SRS_EPSG, OBS_PNT_TOLERANCE,
                                           PRODUCE_DEM=None, PRODUCE_FROM_INDEX=None):
    """
    Imagine-se que se pretende gerar um raster com a visibilidade
    a um conjunto de entidades geográficas identificadas num ficheiro raster
    com o valor 1 (Interest Raster) e que a informação diz respeito a uma
    extensão considerável, como por exemplo, a extensão de um país.
    
    Como é fácil de perceber, isto não pode ser feito executando a ferramenta
    viewshed uma única vez, consequência do elevado volume de dados.
    
    A melhor forma de resolver o problema é segmentar os dados em vários
    ficheiros, tendo como referência uma Feature Classe constituida por features
    que constituem parcelas mais pequenas da área total a ser
    trabalhada - adiante, estas parcelas serão designadas apenas por Células.
    
    A ferramenta viewshed poderá depois ser executada de modo parcelar,
    uma vez para cada conjunto de ficheiros.
    
    Este método segmenta/divide os dados originais em partes, permitindo que a
    viewshed possa ser executada também por partes. Esta divisão seguirá
    as seguintes regras:
    
    * Para cada célula, o DEM deve ser extraído para uma área cuja extensão
    seja igual à extensão da Célula + 10 Km de tolerância;
    
    * Cada célula do Interest Raster será considerada como um ponto de
    observação. Havendo muitos pixéis no Interest Raster, deverá ser definida
    uma tolerância em metros, que definirá a distância mínima entre cada ponto
    de observação. Se esta distância for superior ao cellsize do Interest Raster,
    haverão menos pontos de observação do que células do Interest Raster,
    o que reduzirá significativamente a carga do cálculo da viewshed.
    Claro, esta tolerância deverá ser definida com critério, garantindo que
    os resultados são válidos.
    
    
    Este script tem duas formas de execução:
    * com PRODUCE_DEM = None, será feito o pre_processamento;
    * com PRODUCE_DEM = True, os rasters com as bacias de visibilidade
    serão criados, tendo por base os ficheiros criados no pre-processamento.
    """
    
    import os
    from threading                  import Thread
    from glass.cpu.arcg.mng.rst.proc import clip_raster_each_feat_class
    from glass.cpu.arcg.spanlst.rcls import rcls_folderRaster
    from glass.cpu.arcg.spanlst.surf import viewshed
    from glass.fm                    import tbl_to_obj
    from glass.oss                   import get_filename
    from glass.oss.ops               import create_folder
    from glass.anls.exct             import split_shp_by_attr
    from glass.mng.ext               import df_buffer_extent
    from glass.mng.fld.df            import col_distinct
    
    # Create workspaces to store data
    C_CELLS_FLD = os.path.join(OUT_FOLDER, 'cells')
    RST_TMP     = os.path.join(OUT_FOLDER, 'mask_tmp')
    RST_FLD     = os.path.join(OUT_FOLDER, 'mask_rst')
    B_CELLS_FLD = os.path.join(OUT_FOLDER, 'bf_cells')
    OBS_FLD     = os.path.join(OUT_FOLDER, 'obs_pnt')
    DEM_RST     = os.path.join(OUT_FOLDER, get_filename(DEM))
    
    THRD_MAPS = {
        "INT_RST" : {
            "CELLS_FLD" : create_folder(
                C_CELLS_FLD, overwrite=None) if not os.path.exists(
                    C_CELLS_FLD) else C_CELLS_FLD,
            "RST_TMP"   : create_folder(
                RST_TMP, overwrite=None) if not os.path.exists(
                    RST_TMP) else RST_TMP,
            "RST_FLD"   : create_folder(
                RST_FLD, overwrite=None) if not os.path.exists(
                    RST_FLD) else RST_FLD,
            "OBS_FLD"   : create_folder(
                OBS_FLD, overwrite=None) if not os.path.exists(
                    OBS_FLD) else OBS_FLD
        },
        "DEM"   : {
            "RST_FLD"   : create_folder(
                DEM_RST, overwrite=True) if not os.path.exists(
                    DEM_RST) else DEM_RST,
            "CELLS_FLD" : create_folder(
                B_CELLS_FLD, overwrite=None) if not os.path.exists(
                    B_CELLS_FLD) else B_CELLS_FLD,
        }
    }
    
    if not PRODUCE_DEM:
        """
        Split data into parts
        """
        
        """
        Split Cells
        """
    
        def split_cells(f, bf, of):
            if bf == "DEM":
                _f = df_buffer_extent(
                    f, SRS_EPSG, 10000, os.path.join(OUT_FOLDER, 'bf_cells.shp')
                )
        
            else:
                _f = f
        
            split_shp_by_attr(_f, ID_CELLS, of["CELLS_FLD"], _format='.shp')
    
        thrds = [Thread(
            name="split-{}".format(k), target=split_cells,
            args=(REF_CELLS, k, THRD_MAPS[k])
        ) for k in THRD_MAPS]
    
        for t in thrds:
            t.start()
    
        for t in thrds:
            t.join()
    
        """
        Clip INTEREST RASTER for all cells in CELLS_FLD and BF_CELLS_FLD
        """
    
        for key, val in THRD_MAPS.items():
            inrst = DEM if key == "DEM" else INTEREST_RASTER
        
            clip_raster_each_feat_class(
                inrst, val["CELLS_FLD"],
                val["RST_FLD"] if key == "DEM" else val["RST_TMP"],
                snap=SNAP_RASTER, clipGeometry=True
            )
        
        """
        Reclassify Rasters of interest:
    
        - For each cell, create a Raster with presence of class and other with
        ausence of class
        """
    
        rcls_folderRaster(
            THRD_MAPS["INT_RST"]["RST_TMP"], {0 : 'NoData', 1 : 1},
            THRD_MAPS["INT_RST"]["RST_FLD"]
        )
    
        """
        Create Observer points for each raster
        """
        generalize_obs_points_forFolder(
            THRD_MAPS["INT_RST"]["RST_FLD"], OBS_PNT_TOLERANCE,
            THRD_MAPS["INT_RST"]["OBS_FLD"]
        )
    
    else:
        """
        Generate Viewsheds
        """
    
        cellsDf = tbl_to_obj(REF_CELLS)
    
        LST_CELLS = col_distinct(cellsDf, ID_CELLS)
    
        OBS_REF_NAME = get_filename(REF_CELLS)
    
        __LST_CELLS = LST_CELLS if not PRODUCE_FROM_INDEX else LST_CELLS[:PRODUCE_FROM_INDEX]
    
        for cell_id in LST_CELLS:
            OUT_RST = os.path.join(OUT_FOLDER, "vis_{}.tif".format(str(cell_id)))
        
            if os.path.exists(OUT_RST):
                continue
        
            DEM_RST = os.path.join(
                THRD_MAPS["DEM"]["RST_FLD"], "bf_cells_{}.tif".format(str(cell_id)),
            )
        
            OBS_SHP = os.path.join(
                THRD_MAPS["INT_RST"]["OBS_FLD"],
                "{}_{}.shp".format(OBS_REF_NAME, str(int(cell_id)))
            )
        
            if not os.path.join(OBS_SHP):
                continue
        
            viewshed(
                DEM_RST, OBS_SHP, OUT_RST, snapRaster=DEM_RST, extRaster=DEM_RST
            )


def viewshed_by_feat_class(inRaster, observerDataset, feat_class_folder,
                           output_folder, snapRst=None, visibilityRadius=50000):
    """
    Run viewshed for each feature class in a folder
    
    observerDataset should be a raster or a point/line feature class;
    observerDataset and inRaster should have a major extent than each one
    of the feature class in feat_class_folder
    
    A visibilityRadius is necessary to do a buffer of each feature class.
    Some entity could be outside of the feature class boundary but visible
    from within the same boundary.
    
    Restrictions:
    * ObserverDataset must have a table if a raster;
    
    TO BE MANTAINED?
    """
    
    import arcpy
    import os
    
    arcpy.CheckOutExtension('Spatial')
    
    from glass.oss.ops               import create_folder
    from glass.prop.ff               import vector_formats, raster_formats
    from glass.prop.rst              import get_cellsize, rst_distinct
    from glass.anls.prox.bf          import _buffer
    from glass.cpu.arcg.mng.rst.proc import clip_raster
    from glass.cpu.arcg.spanlst.surf import viewshed
    from glass.cpu.arcg.spanlst.rcls import reclassify
    
    # Check if observerDataset is a Raster or a Feature Class
    # Import methods to clip obserserverDataset
    RASTER_FORMATS = raster_formats()
    VECTOR_FORMATS = vector_formats()
    observerFormat = os.path.splitext(observerDataset)[1]
    
    if observerFormat in VECTOR_FORMATS:
        from glass.cpu.arcg.anls.exct import clip
    
    elif observerFormat in RASTER_FORMATS:
        from glass.to.shp.arcg import rst_to_pnt
        from glass.to.shp import rst_to_polyg
        
        # If Raster, get CELLSIZE of the observer dataset
        CELLSIZE = get_cellsize(observerDataset, gisApi='arcpy')
        REF_CELLSIZE = 500
        
        from glass.cpu.arcg.mng.sample import fishnet
        from glass.cpu.arcg.anls.ovlay import erase
        from glass.cpu.arcg.mng.feat   import feat_to_pnt
    
    else:
        raise ValueError(('Could not identify if observerDataset '
                          'is a raster or a feature class'))
    
    # Create workspace for temporary files
    wTmp = create_folder(os.path.join(output_folder, 'tempfiles'))
    
    # When clipping the observerDataset (when it is a raster), there is a change
    # of obtaining a raster with more values than the original raster
    # Check values of the observerDataset
    UNIQUEVALUES = []
    if observerFormat in RASTER_FORMATS:
        for line in arcpy.SearchCursor(observerDataset):
            value = int(line.getValue("Value"))
            
            if value not in UNIQUEVALUES:
                UNIQUEVALUES.append(value)
            
            else:
                continue
    
    # List feature classes
    arcpy.env.workspace = feat_class_folder
    fclasses = arcpy.ListFeatureClasses()
    
    for fc in fclasses:
        # Create Buffer
        fcBuffer = _buffer(
            fc, visibilityRadius,
            os.path.join(wTmp, os.path.basename(fc)),
            api='arcpy'
        )
        # Clip inRaster
        clipInRst = clip_raster(
            inRaster, fcBuffer,
            os.path.join(wTmp, 'inrst_{}{}'.format(
                os.path.splitext(os.path.basename(fc))[0],
                os.path.splitext(inRaster)[1]
            )), 
            snap=snapRst, clipGeom=True
        )
        
        # Clip observerDataset
        # If Raster, convert to points
        if observerFormat in VECTOR_FORMATS:
            clipObs = clip(
                observerDataset, fcBuffer,
                os.path.join(wTmp, 'obs_{}{}'.format(
                    os.path.splitext(os.path.basename(fc))[0],
                    os.path.splitext(observerDataset)[1]
                ))
            )
        
        elif observerFormat in RASTER_FORMATS:
            # Clip raster
            clipTmp = clip_raster(
                observerDataset, fcBuffer,
                os.path.join(wTmp, 'obs_{}{}'.format(
                    os.path.splitext(os.path.basename(fc))[0],
                    os.path.splitext(observerDataset)[1]
                )), 
                snap=snapRst, clipGeom=None
            )
            
            # Check if clip has the same values as the original raster
            RST_UNIQUE = rst_distinct(clipTmp, gisApi='arcpy')
            if len(RST_UNIQUE) > len(UNIQUEVALUES):
                # Reclassify raster
                rules = {}
                for v in RST_UNIQUE:
                    if v in UNIQUEVALUES:
                        rules[v] = v
                    else:
                        rules[v] = 'NODATA'
                
                clipTmp = reclassify(
                    clipTmp, 'Value', rules,
                    os.path.join(wTmp, 'r_{}'.format(os.path.basename(clipTmp))),
                    template=clipTmp
                )
            
            if CELLSIZE < REF_CELLSIZE:
                # if cellsize if less than REF_CELLSIZE
                # Change cellsize to REF_CELLSIZE:
                
                # 1) Create fishnet REF_CELLSIZE
                fishNet = fishnet(
                    os.path.join(
                        wTmp, 'fish_{}'.format(
                            os.path.basename(fc)
                        )
                    ), clipTmp,
                    cellWidth=REF_CELLSIZE, 
                    cellHeight=REF_CELLSIZE
                )
                
                # 2) Erase areas with NoData values
                # - Raster to shp
                cls_intPolygon = rst_to_polyg(
                    clipTmp, os.path.join(
                        wTmp, 'cls_int_{}'.format(os.path.basename(fc))
                    ), gisApi='arcpy'
                )
                
                # - Erase areas of the fishnet that agrees with nodata values in the raster
                tmpErase = erase(
                    fishNet, cls_intPolygon,
                    os.path.join(wTmp, 'nozones_{}'.format(os.path.basename(fc)))
                )
                trueErase = erase(
                    fishNet, tmpErase,
                    os.path.join(wTmp, 'fishint_{}'.format(os.path.basename(fc)))
                )
                
                # 3) Convert erased fishnet to points
                clipObs = feat_to_pnt(
                    trueErase,
                    os.path.join(wTmp, 'obs_{}'.format(
                        os.path.basename(fc)
                    )),
                    pnt_position="INSIDE"
                )
            
            # Else - simple conversion to points
            else:
                clipObs = rst_to_pnt(
                    clipTmp, os.path.join(wTmp, 'obs_{}'.format(
                        os.path.basename(fc)
                    ))
                )
        
        # Run viewshed
        viewshed(
            clipInRst, clipObs,
            os.path.join(output_folder, 'vis_{}{}'.format(
                os.path.splitext(os.path.basename(fc))[0],
                os.path.splitext(clipInRst)[1]
            ))
        )


def viewshed_by_feat_class2(inRaster, observerDataset, feat_class_folder,
                            output_folder, snapRst=None, visibilityRadius=20000,
                            epsg=3763):
    """
    See for each feature class in a folder if it is possible to see a 
    interest object from all poins in each feature class
    
    Why this method is different from viewshed_by_feat_class?
    viewshed_by_feat_class uses viewshed tool of ArcGIS;
    This one will calculate the visibility point by point, when the script
    identifies that one point is observable from another, it stops.
    
    TO BE MANTAINED?
    """
    
    import arcpy
    import numpy
    import os
    
    from glass.oss.ops               import create_folder
    from glass.prop.ff               import vector_formats, raster_formats
    from glass.cpu.arcg.lyr          import feat_lyr
    from glass.prop.rst              import get_cell_coord
    from glass.prop.ext              import rst_ext
    from glass.prop.rst              import rst_shape, rst_distinct, get_nodata, get_cellsize
    from glass.anls.prox.bf          import _buffer
    from glass.cpu.arcg.mng.rst.proc import clip_raster
    from glass.cpu.arcg.spanlst.surf import viewshed
    from glass.cpu.arcg.spanlst.rcls import reclassify
    from glass.cpu.arcg._3D.view     import line_of_sight
    from glass.to.rst                import shp_to_raster
    from glass.to.rst.arcg           import array_to_raster
    from glass.to.shp.arcg           import geomArray_to_fc
    from glass.fm.rst                import toarray_varcmap as rst_to_array
    
    arcpy.CheckOutExtension('Spatial')
    arcpy.env.overwriteOutput = True
    
    # Check if observerDataset is a Raster or a Feature Class
    RASTER_FORMATS = raster_formats()
    VECTOR_FORMATS = vector_formats()
    observerFormat = os.path.splitext(observerDataset)[1]
    
    if observerFormat in VECTOR_FORMATS:
        from glass.cpu.arcg.anls.exct import clip
    
    elif observerFormat in RASTER_FORMATS:
        from glass.to.shp.arcg import rst_to_pnt
        from glass.to.shp import rst_to_polyg
        
        # If raster, get CELLSIZE of the observer dataset
        CELLSIZE = get_cellsize(observerDataset, gisApi='arcpy')
        REF_CELLSIZE = 500
        
        from glass.cpu.arcg.mng.sample import fishnet
        from glass.cpu.arcg.anls.ovlay import erase
        from glass.cpu.arcg.mng.feat   import feat_to_pnt
    
    else:
        raise ValueError((
            'Could not identify if observerDataset is a raster '
            'or a feature class'
        ))
    
    # Create workspace for temporary files
    wTmp = create_folder(os.path.join(output_folder, 'tempfiles'))
    
    # When clipping the observerDataset (when it is a raster), there is a change
    # of obtaining a raster with more values than the original raster
    # Check values of the observerDataset
    UNIQUEVALUES = []
    if observerFormat in RASTER_FORMATS:
        for line in arcpy.SearchCursor(observerDataset):
            # TODO: Raster could not have attribute table
            value = int(line.getValue("Value"))
            
            if value not in UNIQUEVALUES:
                UNIQUEVALUES.append(value)
            
            else:
                continue
    
    # List feature classes
    arcpy.env.workspace = feat_class_folder
    fclasses = arcpy.ListFeatureClasses()
    
    for fc in fclasses:
        # Create Buffer
        fcBuffer = _buffer(
            fc, visibilityRadius,
            os.path.join(wTmp, os.path.basename(fc)),
        )
        
        # Clip inRaster
        clipInRst = clip_raster(
            inRaster, fcBuffer,
            os.path.join(wTmp, 'dem_{}{}'.format(
                os.path.splitext(os.path.basename(fc))[0],
                os.path.splitext(inRaster)[1]
            )),
            snap=snapRst, clipGeom=True
        )
        
        # Clip observerDataset
        # If Raster, convert to points
        if observerDataset in VECTOR_FORMATS:
            clipObs = clip(
                observerDataset, fcBuffer,
                os.path.join(wTmp, 'obs_{}{}'.format(
                    os.path.splitext(os.path.basename(fc))[0],
                    os.path.splitext(observerDataset)[1]
                ))
            )
        
        elif observerFormat in RASTER_FORMATS:
            # Clip Raster
            clipTmp = clip_raster(
                observerDataset, fcBuffer,
                os.path.join(wTmp, 'obs_{}{}'.format(
                    os.path.splitext(os.path.basename(fc))[0],
                    os.path.splitext(observerDataset)[1]
                )),
                snap=snapRst, clipGeom=True
            )
            
            # Check if clip has the same values that the original raster
            RST_UNIQUE = rst_distinct(clipTmp, gisApi='arcpy')
            if len(RST_UNIQUE) > len(UNIQUEVALUES):
                # Reclassify raster
                rules = {}
                for v in RST_UNIQUE:
                    if v in UNIQUEVALUES:
                        rules[v] = v
                    else:
                        rules[v] = 'NODATA'
                
                clipTmp = reclassify(
                    clipTmp, 'Value', rules,
                    os.path.join(wTmp, 'r_{}'.format(
                        os.path.basename(clipTmp)
                    )),
                    template=clipTmp
                )
            
            if CELLSIZE < REF_CELLSIZE:
                # if cellsize if less than REF_CELLSIZE
                # Change cellsize to REF_CELLSIZE:
                
                # 1) Create fishnet REF_CELLSIZE
                fishNet = fishnet(
                    os.path.join(
                        wTmp, 'fish_{}'.format(os.path.basename(fc))
                    ), clipTmp,
                    cellWidth=REF_CELLSIZE,
                    cellHeight=REF_CELLSIZE
                )
                
                # 2) Erase areas with NoData Values
                # Raster to shp
                cls_intPolygon = rst_to_polyg(
                    clipTmp, os.path.join(
                        wTmp, 'cls_int_{}'.format(os.path.basename(fc))
                    ), gisApi='arcpy'
                )
                
                # - Erase areas of the fishnet that have nodata values
                # in the raster
                tmpErase = erase(
                    fishNet, cls_intPolygon,
                    os.path.join(wTmp, 'nozones_{}'.format(
                        os.path.basename(fc)
                    ))
                )
                
                trueErase = erase(
                    fishNet, tmpErase,
                    os.path.join(wTmp, 'fishint_{}'.format(
                        os.path.basename(fc))
                    )
                )
                
                # 3) Convert erased fishnet to points
                clipObs = feat_to_pnt(
                    trueErase,
                    os.path.join(wTmp, 'obs_{}'.format(
                        os.path.basename(fc)
                    )),
                    pnt_position="INSIDE"
                )
            
            else:
                clipObs = rst_to_pnt(
                    clipTmp, os.path.join(wTmp, 'obs_{}'.format(
                        os.path.basename(fc)
                    ))
                )
        
        # Calculate visibility
        # Boundary to raster
        boundRst = shp_to_raster(
            fc, 'FID', CELLSIZE, None,
            os.path.join(wTmp, '{}_{}'.format(
                os.path.splitext(os.path.basename(fc))[0],
                os.path.splitext(observerDataset)[1]
            )), snap=clipInRst, api='arcpy'
        )
        
        noDataVal = get_nodata(boundRst, gisApi='arcpy')
        
        boundArray = rst_to_array(boundRst)
        
        # Raster to array
        # For each cell, get cell position and create line of sight
        shape = rst_shape(boundRst, gisApi='arcpy')
        xmin, xmax, ymin, ymax = rst_ext(boundRst, gisApi='arcpy2')
        
        visibilityArray = numpy.zeros((shape[0], shape[1]))
        
        numpy.copyto(visibilityArray, boundArray, 'unsafe', boundArray==noDataVal)
        
        for l in range(len(visibilityArray)):
            for c in range(len(visibilityArray[l])):
                if visibilityArray[l][c] == noDataVal:
                    continue
                
                # Get cell position
                x, y = get_cell_coord(
                    l, c, xmin, ymin, CELLSIZE, 
                    CELLSIZE
                )
                
                # Get Line of sight
                cursor = arcpy.SearchCursor(clipObs)
                for line in cursor:
                    FID = line.getValue("FID")
                    geom = line.Shape.centroid
                    sightArray = [
                        {
                            "FID"  : 0,
                            "GEOM" : [(x, y), (geom.X, geom.Y)]
                        },
                    ]
                    
                    lineSight = geomArray_to_fc(
                        sightArray,
                        os.path.join(wTmp, 'ls_{}_{}_{}_{}{}'.format(
                            os.path.splitext(os.path.basename(fc))[0],
                            str(l), str(c),
                            str(FID),
                            os.path.splitext(fc)[1]
                        )),
                        "POLYLINE", epsg
                    )
                    
                    lineSightRes = line_of_sight(
                        clipInRst, lineSight,
                        os.path.join(wTmp, 'lsr_{}_{}_{}_{}{}'.format(
                            os.path.splitext(os.path.basename(fc))[0],
                            str(l), str(c), str(FID),
                            os.path.splitext(fc)[1]
                        ))
                    )
                    
                    lyrLineSight = feat_lyr(lineSightRes)
                    
                    cs = arcpy.SearchCursor(lyrLineSight)
                    lnh = cs.next()
                    cnt = 0
                    while cnt == 0:
                        try:
                            vis = lnh.getValue("TarIsVis")
                        except:
                            pass
                        cnt += 1
                    
                    if vis == 1:
                        visibilityArray[l][c] = 1
                        break
                    else:
                        continue
        
        # Generate Raster with visibility data
        visibilityRst = array_to_raster(
            visibilityArray, xmin, CELLSIZE, CELLSIZE,
            os.path.join(output_folder, 'vis_{}{}'.format(
                os.path.splitext(os.path.basename(fc))[0],
                os.path.splitext(clipInRst)[1]
            ))
        )
        
    return output_folder

