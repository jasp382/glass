"""
Raster statistics by feature 
"""

def statistics_by_line_feat(lines, raster, statistic, new_field):
    """
    Estimates raster statistic per line on a linear feature class
    
    statistic = statistic type (e.g. max, min, mean, sum)
    
    This method has an important problem - depends on the
    number of vertex of each features
    
    TODO: convert lines to raster and use the raster to get the statistics
    of each line
    """
    
    from osgeo           import ogr, gdal
    from glass.geo.gt.prop.ff import drv_name
    from glass.geo.gt.sample  import pnt_val_on_rst
    
    # Open feature class
    shp = ogr.GetDriverByName(
        drv_name(lines)).Open(lines, 1)
    lyr = shp.GetLayer()
    # Create new field
    lyr.CreateField(ogr.FieldDefn(new_field, ogr.OFTReal))
    
    # Open Raster
    img = gdal.Open(raster)
    geo_transform = img.GetGeoTransform()
    band = img.GetRasterBand(1)
    
    # For feature in layer
    for feat in lyr:
        rst_values = []
        # For point in line
        lnh = feat.GetGeometryRef()
        num_pnt = lnh.GetPointCount()
        for pnt in range(num_pnt):
            x, y, z = lnh.GetPoint(pnt)
            cell = pnt_val_on_rst(x, y, band, geo_transform)
            if not cell:
                continue
            else:
                rst_values.append(cell)
        
        if len(rst_values):
            if statistic == 'minimum':
                value = min(rst_values)
            elif statistic == 'maximum':
                value = max(rst_values)
            elif statistic == 'mean':
                value = sum(rst_values) / len(rst_values)
            elif statistic == 'sum':
                value = sum(rst_values)
        
        else:
            continue
        
        feat.SetField(new_field, value)
        lyr.SetFeature(feat)

