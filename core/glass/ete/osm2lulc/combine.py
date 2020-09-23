"""
Methods to update/combine authoritative Land Use/Land Cover Information
with OSM Data
"""


def update_globe_land_cover(
    original_globe_raster, osm_urban_atlas_raster, osm_globe_raster, epsg,
    updated_globe_raster, detailed_globe_raster):
    """
    Update the original Glob Land 30 with the result of the conversion of
    OSM DATA to the Globe Land Cover nomenclature;
    
    Also updates he previous updated Glob Land 30 with the result of the
    conversion of osm data to the Urban Atlas Nomenclature
    """
    
    import os; import numpy as np
    from glass.dct.geo.fmrst    import rst_to_array
    from glass.geo.prop.rst import get_cellsize, get_nodata
    from glass.dct.geo.torst    import obj_to_rst
    
    # ############################# #
    # Convert images to numpy array #
    # ############################# #
    np_globe_original = rst_to_array(original_globe_raster)
    np_globe_osm = rst_to_array(osm_globe_raster)
    np_ua_osm = rst_to_array(osm_urban_atlas_raster)
    
    # ################################## #
    # Check the dimension of both images #
    # ################################## #
    if np_globe_original.shape != np_globe_osm.shape:
        return (
            'The Globe Land 30 raster (original) do not have the same number'
            ' of columns/lines comparing with the Globe Land 30 derived '
            'from OSM data'
        )
    
    elif np_globe_original.shape != np_ua_osm.shape:
        return (
            'The Globe Land 30 raster (original) do not have the same '
            'number of columns/lines comparing with the Urban Atlas raster '
            'derived from OSM data'
        )
    
    elif np_globe_osm.shape != np_ua_osm.shape:
        return (
            'The Globe Land 30 derived from OSM data do not have the same '
            'number of columns/lines comparing with the Urban Atlas raster '
            'derived from OSM data'
        )
    
    # ############## #
    # Check Cellsize #
    # ############## #
    cell_of_rsts = get_cellsize(
        [original_globe_raster, osm_globe_raster, osm_urban_atlas_raster],
        xy=True, gisApi='gdal'
    )
    
    cell_globe_original = cell_of_rsts[original_globe_raster]
    cell_globe_osm = cell_of_rsts[osm_globe_raster]
    cell_ua_osm = cell_of_rsts[osm_urban_atlas_raster]
    
    if cell_globe_original != cell_globe_osm:
        return (
            'The cellsize of the Globe Land 30 raster (original) is not the '
            'same comparing with the Globe Land 30 derived from OSM data'
        )
    
    elif cell_globe_original != cell_ua_osm:
        return (
            'The cellsize of the Globe Land 30 raster (original) is not the '
            'same comparing with the Urban Atlas raster derived from OSM data'
        )
    
    elif cell_ua_osm != cell_globe_osm:
        return (
            'The cellsize of the Globe Land 30 derived from OSM data is not '
            'the same comparing with the Urban Atlas raster derived from '
            'OSM data'
        )
    
    # ############################# #
    # Get the Value of Nodata Cells #
    # ############################# #
    nodata_glob_original = get_nodata(original_globe_raster, gisApi='gdal')
    nodata_glob_osm = get_nodata(osm_globe_raster, gisApi='gdal')
    nodata_ua_osm = get_nodata(osm_urban_atlas_raster, gisApi='gdal')
    
    # ######################################## #
    # Create a new map - Globe Land 30 Updated #
    # ######################################## #
    """
    Create a new array with zeros...
    
    1) The zeros will be replaced by the values in the Globe Land derived from
    OSM.
    
    2) The zeros will be replaced by the values in the Original Globe Land at
    the cells with NULL data in the Globe Land derived from OSM.
    
    The meta array will identify values origins in the updated raster:
    1 - Orinal Raster
    2 - OSM Derived Raster
    """
    
    update_array = np.zeros((
        np_globe_original.shape[0], np_globe_original.shape[1]))
    
    update_meta_array = np.zeros((
        np_globe_original.shape[0], np_globe_original.shape[1]))
    
    # 1)
    np.copyto(update_array, np_globe_osm, 'no', np_globe_osm != nodata_glob_osm)
    # 1) meta
    np.place(update_meta_array, update_array != 0, 2)
    # 2) meta
    np.place(update_meta_array, update_array == 0, 1)
    # 2)
    np.copyto(update_array, np_globe_original, 'no', update_array == 0)
    # 2) meta
    np.place(
        update_meta_array,
        update_array==nodata_glob_original, int(nodata_glob_original)
    )
    # noData to int
    np.place(
        update_array, update_array==nodata_glob_original,
        int(nodata_glob_original)
    )
    
    updated_meta = os.path.join(
        os.path.dirname(updated_globe_raster),
        '{n}_meta{e}'.format(
            n = os.path.splitext(os.path.basename(updated_globe_raster))[0],
            e = os.path.splitext(os.path.basename(updated_globe_raster))[1]
        )
    )
    # Create Updated Globe Cover 30
    obj_to_rst(
        update_array, updated_globe_raster, original_globe_raster,
        noData=int(nodata_glob_original)
    )
    # Create Updated Globe Cover 30 meta
    obj_to_rst(
        update_meta_array, updated_meta, original_globe_raster,
        noData=int(nodata_glob_original)
    )
    
    # ################################################# #
    # Create a new map - Globe Land 30 Detailed with UA #
    # ################################################# #
    np_update = rst_to_array(updated_globe_raster)
    
    detailed_array = np.zeros((np_update.shape[0], np_update.shape[1]))
    
    detailed_meta_array = np.zeros((
        np_update.shape[0], np_update.shape[1]
    ))
    
    """
    Replace 80 Globe Land for 11, 12, 13, 14 of Urban Atlas
    
    The meta array will identify values origins in the detailed raster:
    1 - Updated Raster
    2 - UA Derived Raster from OSM
    """
    # Globe - Mantain some classes
    np.place(detailed_array, np_update==30, 8)
    np.place(detailed_array, np_update==30, 1)
    
    np.place(detailed_array, np_update==40, 9)
    np.place(detailed_array, np_update==40, 1)
    
    np.place(detailed_array, np_update==50, 10)
    np.place(detailed_array, np_update==50, 1)
    
    np.place(detailed_array, np_update==10, 5)
    np.place(detailed_array, np_update==10, 1)
    
    # Water bodies
    np.place(detailed_array, np_ua_osm==50 or np_update==60, 7)
    np.place(detailed_meta_array, np_ua_osm==50 or np_update==60, 1)
    
    # Urban - Where Urban Atlas IS NOT NULL
    np.place(detailed_array, np_ua_osm==11, 1)
    np.place(detailed_meta_array, np_ua_osm==11, 2)
    
    np.place(detailed_array, np_ua_osm==12, 2)
    np.place(detailed_meta_array, np_ua_osm==12, 2)
    
    np.place(detailed_array, np_ua_osm==13, 3)
    np.place(detailed_meta_array, np_ua_osm==13, 2)
    
    np.place(detailed_array, np_ua_osm==14, 4)
    np.place(detailed_meta_array, np_ua_osm==14, 2)
    
    # Urban Atlas - Class 30 to 6
    np.place(detailed_array, np_ua_osm==30, 6)
    np.place(detailed_meta_array, np_ua_osm==30, 2)
    
    # Create Detailed Globe Cover 30
    obj_to_rst(
        detailed_array, detailed_globe_raster, original_globe_raster,
        noData=0
    )
    
    # Create Detailed Globe Cover 30 meta
    detailed_meta = os.path.join(
        os.path.dirname(detailed_globe_raster),
        '{n}_meta{e}'.format(
            n = os.path.splitext(os.path.basename(detailed_meta))[0],
            e = os.path.splitext(os.path.basename(detailed_meta))[1]
        )
    )
    obj_to_rst(
        detailed_meta_array, detailed_meta, original_globe_raster,
        noData=0
    )

