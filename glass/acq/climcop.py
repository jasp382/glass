"""
Climate Copernicus
"""

def get_fwi(geoext, year, months, days, out):
    """
    Get Fire Weather Index data from Copernicus Climate API
    """

    import requests as rqts

    from glass.pys      import obj_to_lst
    from glass.prop.ext import get_ext

    url = "https://ewds.climate.copernicus.eu/api/retrieve/v1/processes/cems-fire-historical-v1"

    months = obj_to_lst(months)
    days   = obj_to_lst(days)

    lft, rgt, bot, top = get_ext(geoext, oepsg=4326)

    param = {
        'product_type'   : 'reanalysis',
        'variable'       : ['fire_weather_index'],
        'dataset_type'   : 'consolidated_dataset',
        'system_version' : '4_1',
        'year'           : f'{year}',
        'month'          : months,
        'day'            : days,
        'grid'           : '0.25/0.25',
        'format'         : 'netcdf',
        'area'           : [top, lft, bot, rgt]
    }

    rsp = rqts.get(url, params=param)

    if rsp.status_code == 200:
        # Save File
        with open(out, 'wb') as file:
            file.write(rsp.content)
        
        return rsp.status_code, out
        
    else:
        print(f"Failed to download data for {year}. Status code: {rsp.status_code}, Message: {rsp.text}")

        return rsp.status_code, rsp.text

