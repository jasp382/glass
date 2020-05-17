"""
Methods to produce Indicators relating Population and their
accessibility to things
"""


def arcg_mean_time_WByPop2(netDt, rdv, infraestruturas, unidades, conjuntos,
                          popf, w, output, oneway=None):
    """
    Tempo medio ponderado pela populacao residente a infra-estrutura mais
    proxima (min)
    
    * netDt = Path to Network Dataset
    * infraestruturas = Points of destiny
    * unidades = BGRI; Freg; Concelhos
    * conjuntos = Freg; Concelhos; NUT - field
    * popf = Field with the population of the statistic unity
    * w = Workspace
    * output = Path to store the final output
    * rdv = Name of feature class with the streets network
    """
    
    import arcpy
    import os
    from gesri.rd.shp       import shp_to_lyr
    from glass.cpu.arcg.mng.feat  import feat_to_pnt
    from gesri.tbl.cols   import add_col, calc_fld
    from glass.cpu.arcg.mng.joins import join_table
    from glass.mng.genze          import dissolve
    from glass.mng.gen            import copy_feat
    from glass.mob.arctbx.closest import closest_facility
    from glass.dct                import tbl_to_obj
    
    def get_freg_denominator(shp, groups, population, fld_time="Total_Minu"):
        cursor = arcpy.SearchCursor(shp)
        
        groups_sum = {}
        for lnh in cursor:
            group = lnh.getValue(groups)
            nrInd = float(lnh.getValue(population))
            time  = float(lnh.getValue(fld_time))
            
            if group not in groups_sum.keys():
                groups_sum[group] = time * nrInd
            
            else:
                groups_sum[group] += time * nrInd
        
        del cursor, lnh
        
        return groups_sum
    
    if not os.path.exists(w):
        from glass.pys.oss import mkdir
        w = mkdir(w, overwrite=False)
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = w
    
    # Start Procedure #
    # Create copy of statitic unities to preserve the original data
    copy_unities = copy_feat(
        unidades,
        os.path.join(w, os.path.basename(unidades)), gisApi='arcpy'
    )
    
    # Generate centroids of the statistic unities - unidades
    lyr_unidades = shp_to_lyr(copy_unities)
    pnt_unidades = feat_to_pnt(lyr_unidades, 'pnt_unidades.shp')
    
    # Network Processing - Distance between CENTROID and Destiny points
    closest_facility(
        netDt, rdv, infraestruturas, pnt_unidades,
        os.path.join(w, "cls_table.dbf"), oneway_restriction=oneway
    )
    add_col("cls_table.dbf", 'j', "SHORT", "6")
    calc_fld("cls_table.dbf", 'j', "[IncidentID]-1")
    join_table(lyr_unidades, "FID", "cls_table.dbf", "j", "Total_Minu")
    del lyr_unidades
    
    # Calculo dos somatorios por freguesia (conjunto)
    # To GeoDf
    unidadesDf = tbl_to_obj(copy_unities)
    
    """
    groups = get_freg_denominator(lyr_unidades, conjuntos, popf)
    add_col(lyr_unidades, "tm", "FLOAT", "10", "3")
    
    cs = arcpy.UpdateCursor(lyr_unidades)
    linha = cs.next()
    while linha:
        group = linha.getValue(conjuntos)
        t = float(linha.getValue("Total_Minu"))
        p = int(linha.getValue(popf))
        total = groups[group]
        indi = ((t * p) / total) * t
        linha.setValue("tm", indi)
        cs.updateRow(linha)
        linha = cs.next()
    
    return dissolve(lyr_unidades, output, conjuntos, "tm SUM")"""
    return unidadesDf


def mean_time_by_influence_area(netDt, rdv, infraestruturas,
                          fld_infraestruturas, unidades, id_unidade,
                          conjuntos, popf, influence_areas_unities, w, output,
                          oneway=True):
    """
    Tempo medio ponderado pela populacao residente a infra-estrutura mais
    proxima (min), por area de influencia
    
    * netDt - Path to Network Dataset
    * infraestruturas - Points of destiny
    * fld_infraestruturas - Field on destiny points to relate with influence area
    * unidades - BGRI; Freg; Concelhos
    * conjuntos - Freg; Concelhos; NUT - field
    * popf - Field with the population of the statistic unity
    * influence_areas_unities - Field on statistic unities layer to relate
    with influence area
    * w = Workspace
    * output = Path to store the final output
    * rdv - Name of feature class with the streets network
    * junctions - Name of feature class with the junctions
    """
    
    import arcpy; import os
    from gesri.rd.shp             import shp_to_lyr
    from glass.cpu.arcg.mng.feat         import feat_to_pnt
    from glass.cpu.arcg.mng.gen          import merge
    from glass.mng.gen                   import copy_feat
    from glass.mng.genze                 import dissolve
    from gesri.tbl.cols          import add_col
    from glass.cpu.arcg.mng.fld          import calc_fld
    from glass.cpu.arcg.mng.fld          import field_statistics
    from gesri.prop.cols  import type_fields
    from glass.cpu.arcg.mng.joins        import join_table
    from glass.cpu.arcg.anls.exct        import select_by_attr
    from glass.cpu.arcg.netanlst.closest import closest_facility
    
    """if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    
    else:
        raise ValueError('Network analyst extension is not avaiable')"""
    
    def ListGroupArea(lyr, fld_ia, fld_grp):
        d = {}
        cs = arcpy.SearchCursor(lyr)
        for lnh in cs:
            id_group = lnh.getValue(fld_grp)
            id_ia = lnh.getValue(fld_ia)
            if id_group not in d.keys():
                d[id_group] = [id_ia]
            else:
                if id_ia not in d[id_group]:
                    d[id_group].append(id_ia)
        return d
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = w
    
    # Procedure #
    copy_unities = copy_feat(
        unidades,
        os.path.join(w, os.path.basename(unidades)), gisApi='arcpy'
    )
    
    # Generate centroids of the statistic unities - unidades
    lyr_unidades = shp_to_lyr(copy_unities)
    pnt_unidades = feat_to_pnt(lyr_unidades, 'pnt_unidades.shp',
                                    pnt_position="INSIDE")
    # List all groups of unities (conjuntos)
    group_areas = ListGroupArea(lyr_unidades, influence_areas_unities, conjuntos)
    # Create Layers
    lyr_pnt_unidades   = shp_to_lyr(pnt_unidades)
    lyr_pnt_facilities = shp_to_lyr(infraestruturas)
    
    result_list = []
    
    fld_type_unities = type_fields(lyr_pnt_unidades, field=conjuntos)
    SELECT_UNITIES = '{fld}=\'{c}\'' if str(fld_type_unities) == 'String' \
        else '{fld}={c}'
    
    fld_type_facilities = type_fields(
        lyr_pnt_facilities, field=fld_infraestruturas)
    SELECT_FACILITIES = '{fld}=\'{obj}\'' if str(fld_type_facilities) == 'String' \
        else '{fld}={obj}'
    for group in group_areas.keys():
        # Select centroids of interest
        interest_centroids = select_by_attr(
            lyr_pnt_unidades,
            SELECT_UNITIES.format(c=str(group), fld=conjuntos),
            'pnt_{c}.shp'.format(c=str(group))
        )
        # Select facilities of interest
        expression = ' OR '.join(
            [SELECT_FACILITIES.format(
                fld=fld_infraestruturas, obj=str(group_areas[group][i])
            ) for i in range(len(group_areas[group]))]
        )
        
        interest_facilities = select_by_attr(
            lyr_pnt_facilities,
            expression,
            'facilities_{c}.shp'.format(c=str(group))
        )
        # Run closest facilitie - Distance between selected CENTROID and selected facilities
        cls_fac_table = os.path.join(w, "clsf_{c}.dbf".format(c=str(group)))
        closest_facility(
            netDt, rdv, interest_facilities, interest_centroids,
            cls_fac_table, oneway_restriction=oneway
        )
        add_col(cls_fac_table, 'j', "SHORT", "6")
        calc_fld(cls_fac_table, 'j', "[IncidentID]-1")
        join_table(interest_centroids, "FID", cls_fac_table, "j", "Total_Minu")
        # Calculate sum of time x population
        add_col(interest_centroids, 'sum', "DOUBLE", "10", "3")
        calc_fld(
            interest_centroids, 'sum',
            "[{pop}]*[Total_Minu]".format(
                pop=popf
            )
        )
        denominador = field_statistics(interest_centroids, 'sum', 'SUM')
        add_col(interest_centroids, 'tm', "DOUBLE", "10", "3")
        calc_fld(
            interest_centroids, 'tm',
            "([sum]/{sumatorio})*[Total_Minu]".format(
                sumatorio=str(denominador)
            )
        )
        result_list.append(interest_centroids)
    
    merge_shp = merge(result_list, "merge_centroids.shp")
    join_table(lyr_unidades, id_unidade, "merge_centroids.shp", id_unidade, "tm")
    
    return dissolve(lyr_unidades, output, conjuntos, statistics="tm SUM", api='arcpy')


def mean_time_in_povoated_areas(network, rdv_name, stat_units, popFld,
                                destinations, output, workspace,
                                ONEWAY=True, GRID_REF_CELLSIZE=10):
    """
    Receive statistical units and some destinations. Estimates the mean distance
    to that destinations for each statistical unit.
    The mean for each statistical will be calculated using a point grid:
    -> Statistical unit to grid point;
    -> Distance from grid point to destination;
    -> Mean of these distances.
    
    This method will only do the math for areas (statistic units)
    with population.
    """
    
    import os; import arcpy
    from gesri.rd.shp       import shp_to_lyr
    from glass.cpu.arcg.anls.exct import select_by_attr
    from glass.cpu.arcg.mng.fld   import field_statistics
    from gesri.tbl.cols   import add_col
    from glass.cpu.arcg.mng.gen   import merge
    from glass.mng.gen            import copy_feat
    from glass.mob.arctbx.closest import closest_facility
    from glass.to.shp.arcg        import rst_to_pnt
    from glass.to.rst             import shp_to_raster
    
    if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    
    else:
        raise ValueError('Network analyst extension is not avaiable')
    
    arcpy.env.overwriteOutput = True
    
    WORK = workspace
    
    # Add field
    stat_units = copy_feat(
        stat_units, os.path.join(WORK, os.path.basename(stat_units)),
        gisApi='arcpy'
    )
    add_col(stat_units, "TIME", "DOUBLE", "10", precision="3")
    
    # Split stat_units into two layers
    # One with population
    # One with no population
    withPop = select_by_attr(stat_units, '{}>0'.format(popFld),
                             os.path.join(WORK, 'with_pop.shp'))
    noPop   = select_by_attr(stat_units, '{}=0'.format(popFld),
                             os.path.join(WORK, 'no_pop.shp'))
    
    # For each statistic unit with population
    withLyr = shp_to_lyr(withPop)
    cursor  = arcpy.UpdateCursor(withLyr)
    
    FID = 0
    for feature in cursor:
        # Create a new file
        unity = select_by_attr(
            withLyr, 'FID = {}'.format(str(FID)),
            os.path.join(WORK, 'unit_{}.shp'.format(str(FID)))
        )
        
        # Convert to raster
        rst_unity = shp_to_raster(
            unity, "FID", GRID_REF_CELLSIZE, None,
            os.path.join(WORK, 'unit_{}.tif'.format(str(FID))), api='arcpy'
        )
        
        # Convert to point
        pnt_unity = rst_to_pnt(
            rst_unity, 
            os.path.join(WORK, 'pnt_un_{}.shp'.format(str(FID)))
        )
        
        # Execute closest facilitie
        CLOSEST_TABLE = os.path.join(
            WORK, 'cls_fac_{}.dbf'.format(str(FID))
        )
        closest_facility(
            network, rdv_name, destinations, pnt_unity,
            CLOSEST_TABLE, 
            oneway_restriction=ONEWAY
        )
        
        # Get Mean
        MEAN_TIME = field_statistics(CLOSEST_TABLE, 'Total_Minu', 'MEAN')[0]
        
        # Record Mean
        feature.setValue("TIME", MEAN_TIME)
        cursor.updateRow(feature)
        
        FID += 1
    
    merge([withPop, noPop], output)
    
    return output


def population_within_point_buffer(netDataset, rdvName, pointShp, populationShp,
                                   popField, bufferDist, epsg, output,
                                   workspace=None, bufferIsTimeMinutes=None,
                                   useOneway=None):
    """
    Assign to points the population within a certain distance (metric or time)
    
    * Creates a Service Area Polygon for each point in pointShp;
    * Intersect the Service Area Polygons with the populationShp;
    * Count the number of persons within each Service Area Polygon
    (this number will be weighted by the area % of the statistic unit
    intersected with the Service Area Polygon).
    """
    
    import arcpy; import os
    from geopandas                import GeoDataFrame
    from gesri.rd.shp        import shp_to_lyr
    from glass.cpu.arcg.anls.ovlay import intersect
    from glass.mng.gen             import copy_feat
    from glass.cpu.arcg.mng.fld    import add_geom_attr
    from glass.cpu.arcg.mng.fld    import calc_fld
    from glass.mng.genze           import dissolve
    from glass.mob.arctbx.svarea   import service_area_use_meters
    from glass.mob.arctbx.svarea   import service_area_polygon
    from glass.fm                  import tbl_to_obj
    from glass.toshp               import df_to_shp
    
    workspace = os.path.dirname(pointShp) if not workspace else workspace
    
    if not os.path.exists(workspace):
        from glass.oss.ops import create_folder
        workspace = create_folder(workspace, overwrite=False)
    
    # Copy population layer
    populationShp = copy_feat(populationShp, os.path.join(
        workspace, 'cop_{}'.format(os.path.basename(populationShp))
    ), gisApi='arcpy')
    
    # Create layer
    pntLyr = shp_to_lyr(pointShp)
    popLyr = shp_to_lyr(populationShp)
    
    # Create Service Area
    if not bufferIsTimeMinutes:
        servArea = service_area_use_meters(
            netDataset, rdvName, bufferDist, pointShp,
            os.path.join(workspace, 'servare_{}'.format(
                os.path.basename(pointShp))),
            OVERLAP=False, ONEWAY=useOneway
        )
    
    else:
        servArea = service_area_polygon(
            netDataset, rdvName, bufferDist, pointShp,
            os.path.join(workspace, "servare_{}".format(
                os.path.basename(pointShp))),
            ONEWAY_RESTRICTION=useOneway, OVERLAP=None
        )
    
    servAreaLyr = shp_to_lyr(servArea)
    
    # Add Column with Polygons area to Feature Class population
    add_geom_attr(popLyr, "total", geom_attr="AREA")
    
    # Intersect buffer and Population Feature Class
    intSrc = intersect([servAreaLyr, popLyr], os.path.join(
        workspace, "int_servarea_pop.shp"
    ))
    
    intLyr = shp_to_lyr(intSrc)
    
    # Get area of intersected statistical unities with population
    add_geom_attr(intLyr, "partarea", geom_attr="AREA")
    
    # Get population weighted by area intersected
    calc_fld(
        intLyr, "population",
        "((([partarea] * 100) / [total]) * [{}]) / 100".format(popField),
        {"TYPE" : "DOUBLE", "LENGTH" : "10", "PRECISION" : "3"}
    )
    
    # Dissolve service area by Facility ID
    diss = dissolve(
        intLyr, os.path.join(workspace, 'diss_servpop.shp'),
        "FacilityID", statistics="population SUM"
    )
    
    # Get original Point FID from FacilityID
    calc_fld(
        diss, "pnt_fid", "[FacilityID] - 1",
        {"TYPE" : "INTEGER", "LENGTH" : "5", "PRECISION" : None}
    )
    
    dfPnt  = tbl_to_obj(pointShp)
    dfDiss = tbl_to_obj(diss)
    
    dfDiss.rename(columns={"SUM_popula": "n_pessoas"}, inplace=True)
    
    resultDf = dfPnt.merge(
        dfDiss, how='inner', left_index=True, right_on="pnt_fid"
    )
    
    resultDf.drop('geometry_y', axis=1, inplace=True)
    
    resultDf = GeoDataFrame(
        resultDf, crs={'init' : 'epsg:{}'.format(epsg)},
        geometry='geometry_x'
    )
    
    df_to_shp(resultDf, output)
    
    return output
