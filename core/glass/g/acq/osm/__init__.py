"""
Methods to extract OSM data from the internet
"""


def download_by_boundary(input_boundary, folder_out, osm_name, epsg,
                         GetUrl=True, db_name=None, geomCol=None,
                         justOneFeature=None):
    """
    Download data from OSM using a bounding box
    and OSM Overpass API
    """
    
    import os
    from osgeo         import ogr
    from glass.pys.web import get_file
    from glass.pys.oss import os_name
    
    OS_NAME = os_name()
    
    EXTENTS = []
    
    if db_name and geomCol:
        """
        Assuming input_boundary is a PostgreSQL Table
        """
        
        from glass.pys        import obj_to_lst
        from glass.g.prop.gql import tbl_ext
        
        for t in obj_to_lst(input_boundary):
            EXTENTS.append(tbl_ext(db_name, t, geomCol))
    
    else:
        if type(input_boundary) == dict:
            if 'top' in input_boundary and 'bottom' in input_boundary \
                and 'left' in input_boundary and 'right' in input_boundary:
                
                EXTENTS.append([
                    input_boundary['left'],input_boundary['right'],
                    input_boundary['bottom'], input_boundary['top']
                ])
        
            else:
                raise ValueError((
                    'input_boundary is a dict but the keys are not correct. '
                    'Please use left, right, top and bottom as keys'
                ))
    
        elif type(input_boundary) == list:
            if len(input_boundary) == 4:
                EXTENTS.append(input_boundary)
        
            else:
                raise ValueError((
                    'input boundary is a list with more than 4 objects. '
                    'The list should be like: '
                    'l = [left, right, bottom, top]'
                ))
    
        elif type(input_boundary) == ogr.Geometry:
            EXTENTS.append(input_boundary.GetEnvelope())
    
        else:
            # Assuming input boundary is a file
        
            #Check if file exists
            if not os.path.exists(input_boundary):
                raise ValueError((
                    "Sorry, but the file {} does not exist inside the folder {}!"
                ).format(
                    os.path.basename(input_boundary),
                    os.path.dirname(input_boundary)
                ))
        
            # Check if is a raster
            from glass.g.prop import check_isRaster
            isRst = check_isRaster(input_boundary)
        
            # Get EPSG
            if not epsg:
                from glass.g.prop.prj import get_epsg
            
                epsg = get_epsg(input_boundary)
        
            if isRst:
                from glass.g.prop.rst import rst_ext
            
                # Get raster extent
                EXTENTS.append(rst_ext(input_boundary))
        
            else:
                from glass.g.prop import drv_name
                
                # Todo: check if it is shape
                
                # Open Dataset
                inSrc = ogr.GetDriverByName(drv_name(
                    input_boundary)).Open(input_boundary)
                
                lyr = inSrc.GetLayer()
                
                i = 1
                for feat in lyr:
                    geom = feat.GetGeometryRef()
                    
                    featext = geom.GetEnvelope()
                    
                    EXTENTS.append(featext)
                    
                    if justOneFeature:
                        break
    
    if epsg != 4326:
        from glass.g.gobj import new_pnt
        from glass.g.prj.obj  import prj_ogrgeom
        
        for i in range(len(EXTENTS)):
            bottom_left = prj_ogrgeom(new_pnt(
                EXTENTS[i][0], EXTENTS[i][2]), epsg, 4326)
        
            top_right   = prj_ogrgeom(new_pnt(
                EXTENTS[i][1], EXTENTS[i][3]), epsg, 4326)
        
            left , bottom = bottom_left.GetX(), bottom_left.GetY()
            right, top    = top_right.GetX()  , top_right.GetY()
            
            EXTENTS[i] = [left, right, bottom, top]
    
    #url = "https://overpass-api.de/api/map?bbox={}"
    url = "https://lz4.overpass-api.de/api/interpreter?bbox={}"
    
    RESULTS = []
    for e in range(len(EXTENTS)):
        bbox_str = ','.join([str(p) for p in EXTENTS[e]])
        
        if GetUrl:
            RESULTS.append(url.format(bbox_str))
            continue
        
        if len(EXTENTS) == 1:
            outOsm = os.path.join(folder_out, osm_name + '.xml')
        else:
            outOsm = os.path.join(folder_out, "{}_{}.xml".format(osm_name, str(e)))
        
        osm_file = get_file(
            url.format(bbox_str), outOsm,
            useWget=None if OS_NAME == 'Windows' else None
        )
        
        RESULTS.append(osm_file)
    
    return RESULTS[0] if len(RESULTS) == 1 else RESULTS


def osm_from_geofabrik(out_folder):
    """
    Get all OSM Files in GeoFabrik
    """
    
    import os
    from glass.pys.web  import get_file
    from glass.cons.osm import osm_files
    from glass.pys.oss  import mkdir

    main_url = "http://download.geofabrik.de/{}/{}-latest.osm.pbf"

    for c in osm_files:
        if c == 'russia':
            get_file(
                "http://download.geofabrik.de/russia-latest.osm.pbf",
                os.path.join(out_folder, "russia-latest.osm.pbf")
            )
            continue
        
        # Create folder for that continent
        cf = mkdir(os.path.join(out_folder, c))

        # Download files of every continent
        for _c in osm_files[c]:
            get_file(main_url.format(c, _c), os.path.join(
                cf, 
                "{}-latest.osm.pbf".format(_c.replace('/', '_'))
            ), useWget=True)

    return out_folder

