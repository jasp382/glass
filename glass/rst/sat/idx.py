"""
Apply Indexes to highligh LULC types in Satellite Imagery

Use GDAL to apply index
"""

import os
import numpy        as np
from osgeo          import gdal
from glass.wenv.grs import grass_session
from glass.pys.tm   import now_as_str

from glass.prop.img import rst_epsg
from glass.wt.rst import obj_to_rst
from glass.rst.alg import grsrstcalc
from glass.it.rst import grs_to_rst


class CalcIndexes:
    """
    Apply radiometric indexes

    - NDVI: Normalized Difference NIR/Red Normalized Difference
    Vegetation Index, Calibrated NDVI - CDVI

    https://www.indexdatabase.de/db/i-single.php?id=58
    
    EXPRESSION: (nir - red) / (nir + red)
    """

    sensors = ["sentinel-2", "landsat-8"]
    apis = ["grass", "pygdal"]
    avl_idxs = [
        # Water Indexes
        "ndwi", "swi",
        # Vegetation Indexes
        "ndvi", "nbr", "evi",
        "savi_regular", "savi_adjusted", "savi_modified",
        "ndre", "ngrdi", "chlrd", "ndci",
        "gndvi", "coloration",
        # Burn areas
        "mirbi",
        "sani",
        "sasi",
        "anir",
        # Built up
        "ndbi",
        # Snow
        "ndsi",
        # Normalized Burn Ratio
        "nbr",
        "mndwi",
        "savi"
    ]
    sensors_bands = {
        "sentinel-2" : ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B11', 'B12'],
        "landsat-8"  : []
    }
    bands_ref = {
        'blue'  : {'sentinel-2' : 'B02'},
        'green' : {'sentinel-2' : 'B03'},
        'red'   : {'sentinel-2' : 'B04'},
        'nir'   : {'sentinel-2' : 'B08'},
        'swir1' : {'sentinel-2' : 'B11'},
        'swir2' : {'sentinel-2' : 'B12'}
    }

    bands_center = {
        'red'   : {'sentinel-2' : '665'},
        'nir'   : {'sentinel-2' : '842'},
        'swir1' : {'sentinel-2' : '1610'},
        'swir2' : {'sentinel-2' : '2190'}
    }

    idxs = {}
    idxs_nd = {}

    ws = None

    def __init__(self, sensor: str, api: str, gws:None|str=None):

        if sensor not in self.sensors:
            raise ValueError("Sensor value is not valid - options are: sentinel-2 and landsat-8")
        
        if api not in self.apis:
            raise ValueError("API value is not valid - options are: grass and pygdal")

        self.sensor = sensor
        self.api    = api
        self.avlbnd = self.sensors_bands[self.sensor]

        self.ws = gws
    
    def get_band_center(self, bandname: str):
        if bandname not in self.bands_center or self.sensor not in self.bands_center[bandname]:
            raise ValueError(f'{bandname} center value is not available')
    
        return self.bands_center[bandname][self.sensor]
    
    def get_band_data(self, bandname: str):
        
        if self.bands_ref[bandname][self.sensor] not in self.bands_data:
            raise ValueError(f'{bandname} band is not available')
            
        return self.bands_data[self.bands_ref[bandname][self.sensor]]
    
    def get_band_nd(self, bandname: str):
        if self.bands_ref[bandname][self.sensor] not in self.nodata_val:
            raise ValueError(f'{bandname} band is not available')
        
        return self.nodata_val[self.bands_ref[bandname][self.sensor]]
    
    def gdal_read_data(self, _bands:dict[str, str]):
        """
        Read bands using PyGDAL
        """

        data, nds = {}, {}

        c = 0
        for band in self.avlbnd:
            if band not in _bands:
                continue

            src = gdal.Open(_bands[band], gdal.GA_ReadOnly)

            if not c:
                self.geotrans = src.GetGeoTransform()
                self.epsg = rst_epsg(src)
                c += 1

            num = src.GetRasterBand(1).ReadAsArray().astype(float)
            nd = src.GetRasterBand(1).GetNoDataValue()

            #srcs[band] = src
            data[band] = num
            nds[band] = nd
        
        return data, nds
    
    def grass_read_data(self, _bands:dict[str, str]):
        data = {}

        # Create GRASS GIS Session
        rb = list(_bands.values())[0]

        ws = os.path.dirname(rb) if not self.ws else \
            self.ws
        
        print(ws)
        loc = now_as_str(utc=True)

        gb = grass_session(ws, loc=loc, srs=rb)

        # Import data into GRASS GIS
        from glass.it.rst import rst_to_grs

        for band in self.avlbnd:
            if band not in _bands:
                continue

            data[band] = rst_to_grs(_bands[band])
        
        return data
    
    def read_data(self, bands: dict[str, str]):
        """
        Read Bands
        """

        if self.api == 'pygdal':
            self.bands_data, self.nodata_val = self.gdal_read_data(bands)
        
        elif self.api == 'grass':
            self.bands_data = self.grass_read_data(bands)
        
        else:
            return False
        
        return True
    
    def gdal_calc_idx(self, idx: str):
        """
        Calculate Index using PyGDAL
        """

        bdata, nds = [], []

        if idx == 'ndwi':
            nir   = self.get_band_data('nir')
            green = self.get_band_data("green")

            bdata.append(nir)
            bdata.append(green)

            nds.append(self.get_band_nd('nir'))
            nds.append(self.get_band_nd('green'))

            den = green + nir
            result = np.where(
                den == 0, 100,
                (green - nir) / den
            )
        
        elif idx == 'ndvi':
            nir = self.get_band_data('nir')
            red = self.get_band_data('red')

            bdata.append(nir)
            bdata.append(red)

            nds.append(self.get_band_nd('nir'))
            nds.append(self.get_band_nd('red'))

            den = (nir + red)
            result = np.where(
                den == 0, 100,
                (nir - red) / den
            )
        
        elif idx == 'swi':
            swir = self.get_band_data('swir1')
            blue = self.get_band_data('blue')

            bdata.append(swir)
            bdata.append(blue)

            nds.append(self.get_band_nd('swir1'))
            nds.append(self.get_band_nd('blue'))

            den = np.sqrt(blue - swir)

            result = np.where(
                den == 0, 100,
                1 / den
            )
        
        elif idx == 'evi':
            nir = self.get_band_data('nir')
            red = self.get_band_data('red')
            blu = self.get_band_data('blue')

            deno = (nir + 6.0 * red - 7.5 * blu + 1)

            result = np.where(
                deno == 0, 100,
                2.5 * (nir - red) / (deno)
            )

        # Place NoData Value
        nd = np.amin(result) - 1

        for b in bdata:
            np.place(result, b == 0, nd)
        
        for v in nds:
            np.place(result, b == v, nd)
        
        np.place(result, result == 100, nd)
        
        self.idxs[idx] = result
        self.idxs_nd[idx] = nd
    
    def grass_calc_idx(self, idx: str):
        exp = ''

        if idx == 'ndwi':
            nir = self.get_band_data('nir')
            green = self.get_band_data('green')

            exp = f'({green} - float({nir})) / ({green} + float({nir}))'

            nd = -2
        
        elif idx == 'ndvi':
            nir = self.get_band_data('nir')
            red = self.get_band_data('red')

            exp = f'({nir} - float({red})) / ({nir} + float({red}))'

            nd = -2
        
        elif idx == 'swi':
            swir = self.get_band_data('swir1')
            blue = self.get_band_data('blue')

            exp = f'1 / sqrt({blue} - {swir})'

            nd = -1
        
        elif idx == 'evi':
            nir = self.get_band_data('nir')
            red = self.get_band_data('red')
            blu = self.get_band_data('blue')

            deno = f"({nir} + 6.0 * {red} - 7.5 * {blu} + 1)"

            exp = f"2.5 * ({nir} - {red}) / {deno}"

            nd = -1000000
        
        elif idx == 'nbr':
            nir = self.get_band_data('nir')
            swir = self.get_band_data('swir2')

            exp = f'({nir} - float({swir})) / ({nir} + float({swir}))'

            nd = -2
        
        elif idx == 'ndbi':
            nir = self.get_band_data('nir')
            swir = self.get_band_data('swir1')

            exp = f'({swir} - float({nir})) / ({swir} + float({nir}))'

            nd = -2
        
        elif idx == 'mndwi':
            green = self.get_band_data('green')
            swir = self.get_band_data('swir1')

            exp = f'({green} - float({swir})) / ({green} + float({swir}))'

            nd = -2
        
        elif idx == 'savi':
            #L = 0.428 # L varies from -0,9 and 1,6
            L = 0.5

            red = self.get_band_data('red')
            nir = self.get_band_data('nir')

            exp = f'(({nir} - {red}) / ({nir} + {red} + {str(L)})) * (1 + {str(L)})'

            nd = -1000000
        
        elif idx == 'mirbi':
            sswir = self.get_band_data("swir1")
            lswir = self.get_band_data("swir2")

            exp = f'10 * {lswir} - 9.8 * {sswir} + 2'

            nd = -1000000
        
        elif idx == 'sani':
            nir   = self.get_band_data("nir")
            sswir = self.get_band_data("swir1")
            lswir = self.get_band_data("swir2")

            nir_center   = self.get_band_center('nir')
            sswir_center = self.get_band_center('swir1')
            lswir_center = self.get_band_center('swir2')

            a = f'sqrt(pow({nir_center} - {sswir_center}, 2) + pow({nir} - {sswir}, 2))'
            b = f'sqrt(pow({sswir_center} - {lswir_center}, 2) + pow({sswir} - {lswir}, 2))'
            c = f'sqrt(pow({lswir_center} - {nir_center}, 2) + pow({lswir} - {nir}, 2))'

            exp = f'(({lswir} - {nir}) / ({lswir} + {nir})) * ' + \
                f"(acos(((pow({a}, 2) + pow({b}, 2) - pow({c}, 2)) / (2 * {a} * {b}))) " + \
                    "* (3.141592653589793 / 180))"
            
            nd = -1000000
        
        elif idx == 'sasi':
            nir   = self.get_band_data("nir")
            sswir = self.get_band_data("swir1")
            lswir = self.get_band_data("swir2")

            nir_center   = self.get_band_center('nir')
            sswir_center = self.get_band_center('swir1')
            lswir_center = self.get_band_center('swir2')

            a = f'sqrt(pow({nir_center} - {sswir_center}, 2) + pow({nir} - {sswir}, 2))'
            b = f'sqrt(pow({sswir_center} - {lswir_center}, 2) + pow({sswir} - {lswir}, 2))'
            c = f'sqrt(pow({lswir_center} - {nir_center}, 2) + pow({lswir} - {nir}, 2))'

            exp = f"(acos(((pow({a}, 2) + pow({b}, 2) - pow({c}, 2)) / (2 * {a} * {b}))) " + \
                f"* (3.141592653589793 / 180)) * ({sswir} - {nir})"
            
            nd = -1000000
        
        elif idx == 'anir':
            nir   = self.get_band_data("nir")
            sswir = self.get_band_data("swir1")
            red   = self.get_band_data("red")

            nir_center   = self.get_band_center('nir')
            sswir_center = self.get_band_center('swir1')
            red_center = self.get_band_center('red')

            a = f'sqrt(pow({red_center} - {nir_center}, 2) + pow({red} - {nir}, 2))'
            b = f'sqrt(pow({nir_center} - {sswir_center}, 2) + pow({nir} - {sswir}, 2))'
            c = f'sqrt(pow({sswir_center} - {red_center}, 2) + pow({sswir} - {red}, 2))'

            exp = f"(acos(((pow({a}, 2) + pow({b}, 2) - pow({c}, 2)) / (2 * {a} * {b}))) " + \
                f"* (3.141592653589793 / 180))"
            
            nd = -1000000

        self.idxs[idx] = grsrstcalc(exp, f'rst_{idx}', ascmd=True)
        self.idxs_nd[idx] = nd
    
    def calc_idx(self, idx_name: str):

        if idx_name not in self.avl_idxs:
            raise ValueError((
                f"{idx_name} is not a valid option. "
                f"Valid options are: {', '.join(self.avl_idxs)}"
            ))
        
        if self.api == 'pygdal':
            self.gdal_calc_idx(idx_name)
        
        elif self.api == 'grass':
            self.grass_calc_idx(idx_name)
        
        else:
            return False
        
        return True
    
    def export_result(self, idx: str, out: str):
        if self.api == 'pygdal':
            obj_to_rst(
                self.idxs[idx], out,
                self.geotrans, self.epsg,
                noData=self.idxs_nd[idx]   
            )
        
        elif self.api == 'grass':
            grs_to_rst(
                self.idxs[idx], out, as_cmd=True,
                dtype="Float64", nodata=self.idxs_nd[idx]
            )

        else:
            return None
        
        return out


def calc_nbr(nir, swir, outrst):
    """
    Normalized Burn Ratio
    
    EXPRESSION Sentinel-2A: (8-12) / (8+12)

    https://custom-scripts.sentinel-hub.com/sentinel-2/nbr/
    """
    
    # Open Images
    snir  = gdal.Open(nir, gdal.GA_ReadOnly)
    _swir = gdal.Open(swir, gdal.GA_ReadOnly)
    
    # To Array
    nnir  = snir.GetRasterBand(1).ReadAsArray().astype(float)
    nwir = _swir.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    den = nnir + nwir
    nbr = np.where(
        den == 0, 100,
        (nnir - nwir) / den
    )
    
    # Place NoData Value
    nir_nd = snir.GetRasterBand(1).GetNoDataValue()
    wir_nd = _swir.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(nbr) - 1

    np.place(nbr, den == 0, nd)
    
    np.place(nbr, nnir == nir_nd, nd)
    np.place(nbr, nwir == wir_nd, nd)
    
    # Export Result
    return obj_to_rst(
        nbr, outrst, snir.GetGeoTransform(),
        rst_epsg(snir), noData=nd
    )


def calc_savi(nir, red, out, formula='regular'):
    """
    Apply Soil Adjusted Vegetation

    * regular - https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=87
    * adjusted - https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=209
    * modified
    """

    opt = ['regular', 'adjusted', 'modified']

    formula = 'regular' if formula not in opt else formula

    # Open Images
    snir = gdal.Open(nir, gdal.GA_ReadOnly)
    sred = gdal.Open(red, gdal.GA_ReadOnly)

    # To Array
    nnir = snir.GetRasterBand(1).ReadAsArray().astype(float)
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)

    # Do calculation
    L = 0.428 # L varies from -0,9 and 1,6
    if formula == 'regular':
        savi = ((nnir - nred) / (nnir + nred + L)) * (1 + L)
    
    elif formula == 'adjusted':
        n = nnir - 1.22 * nred - 0.03
        d = 1.22 * nnir + nred - 1.22 * 0.03 + 0.08 * (1 + 1.22**2)

        savi = 1.22 * (n/d)
    
    elif formula == 'modified':
        n = np.power(2 * nnir + 1, 2) - 8 * (nnir - nred)
        nsqrt = np.sqrt(n)

        savi = (2 * nnir + 1 - nsqrt) / 2

    # Place NoData Value
    nir_nd = snir.GetRasterBand(1).GetNoDataValue()
    red_nd = sred.GetRasterBand(1).GetNoDataValue()
    
    savi_nd = np.amin(savi) - 1
    
    np.place(savi, nnir==0, savi_nd)
    np.place(savi, nred==0, savi_nd)

    np.place(savi, nnir==nir_nd, savi_nd)
    np.place(savi, nred==red_nd, savi_nd)
    
    # Export Result
    return obj_to_rst(
        savi, out, snir.GetGeoTransform(),
        rst_epsg(snir), noData=savi_nd
    )




def calc_evi(nir, red, blue, out):
    """
    Apply Enhanced Vegetation Index
    """

    d = {'n' : nir, 'r' : red, 'b' : blue}

    # Open Images
    src = {k: gdal.Open(d[k], gdal.GA_ReadOnly) for k in d}

    # To Array
    num = {k: src[k].GetRasterBand(
        1).ReadAsArray().astype(float) for k in d}

    # Do calculation
    deno = (num['n'] + 6.0 * num['r'] - 7.5 * num['b']) + 1.0
    evi = np.where(
        deno == 0, -1,
        2.5 * ((num['n'] - num['r']) / deno)
    )

    # Place NoData Value
    evi_nd = np.amin(evi) - 1

    for k in d:
        nd = src[k].GetRasterBand(1).GetNoDataValue()

        np.place(evi, num[k]==nd, evi_nd)
    
    np.place(evi, deno == 0, evi_nd)
    np.place(evi, evi < -1, -1)
    np.place(evi, evi > 1, 1)
    
    # Export Result
    return obj_to_rst(
        evi, out, src['n'].GetGeoTransform(),
        rst_epsg(src['n']), noData=evi_nd
    )


def calc_ndre(nir, re, out):
    """
    Apply Normalized Difference Red Edge
    """

    # Open Images
    snir = gdal.Open(nir, gdal.GA_ReadOnly)
    sre  = gdal.Open(re, gdal.GA_ReadOnly)
    
    # To Array
    nnir = snir.GetRasterBand(1).ReadAsArray().astype(float)
    nre  = sre.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    ndre = (nnir - nre) / (nnir + nre)
    
    # Place NoData Value
    nir_nd = snir.GetRasterBand(1).GetNoDataValue()
    re_nd  = sre.GetRasterBand(1).GetNoDataValue()
    
    ndre_nd = np.amin(ndre) - 1
    
    np.place(ndre, nnir==nir_nd, ndre_nd)
    np.place(ndre, nre==re_nd, ndre_nd)
    
    # Export Result
    return obj_to_rst(
        ndre, out, snir.GetGeoTransform(),
        rst_epsg(snir), noData=ndre_nd
    )


def calc_ngrdi(green, red, out):
    """
    Apply Normalized Green/Red Vegetation Index
    """

    # Open Images
    sgre = gdal.Open(green, gdal.GA_ReadOnly)
    sred = gdal.Open(red, gdal.GA_ReadOnly)
    
    # To Array
    ngre = sgre.GetRasterBand(1).ReadAsArray().astype(float)
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    den = ngre + nred
    ngrdi = np.where(
        den == 0, 100,
        (ngre - nred) / den
    )
    
    # Place NoData Value
    green_nd = sgre.GetRasterBand(1).GetNoDataValue()
    red_nd   = sred.GetRasterBand(1).GetNoDataValue()
    
    ngrdi_nd = np.amin(ngrdi) - 1

    np.place(ngrdi, den == 0, ngrdi_nd)
    
    np.place(ngrdi, ngre==green_nd, ngrdi_nd)
    np.place(ngrdi, nred==red_nd, ngrdi_nd)
    
    # Export Result
    return obj_to_rst(
        ngrdi, out, sgre.GetGeoTransform(),
        rst_epsg(sgre), noData=ngrdi_nd
    )


def calc_ndbi(swir, nir, out):
    """
    Apply Normalized Difference Build Index
    """

    # Open Images
    sswir = gdal.Open(swir, gdal.GA_ReadOnly)
    snir  = gdal.Open(nir, gdal.GA_ReadOnly)
    
    # To Array
    nswir = sswir.GetRasterBand(1).ReadAsArray().astype(float)
    nnir  = snir.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    den = nswir + nnir
    ndbi = np.where(
        den == 0, 100,
        (nswir - nnir) / den
    )
    
    # Place NoData Value
    swir_nd = sswir.GetRasterBand(1).GetNoDataValue()
    nir_nd  = snir.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(ndbi) - 1

    np.place(ndbi, den == 0, nd)
    
    np.place(ndbi, nswir==swir_nd, nd)
    np.place(ndbi, nnir==nir_nd, nd)
    
    # Export Result
    return obj_to_rst(
        ndbi, out, sswir.GetGeoTransform(),
        rst_epsg(sswir), noData=nd
    )


def calc_ndsi(b03, b11, out):
    """
    Apply Normalized Difference Snow Index

    https://custom-scripts.sentinel-hub.com/sentinel-2/ndsi/
    https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/level-2a/algorithm-overview
    """

    # Open Images
    sb03 = gdal.Open(b03, gdal.GA_ReadOnly)
    sb11 = gdal.Open(b11, gdal.GA_ReadOnly)
    
    # To Array
    nb03 = sb03.GetRasterBand(1).ReadAsArray().astype(float)
    nb11 = sb11.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    den = nb03 + nb11
    ndsi = np.where(
        den == 0, 100,
        (nb03 - nb11) / den
    )
    
    # Place NoData Value
    b03nd = sb03.GetRasterBand(1).GetNoDataValue()
    b11nd = sb11.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(ndsi) - 1

    np.place(ndsi, den == 0, nd)
    
    np.place(ndsi, nb03==b03nd, nd)
    np.place(ndsi, nb11==b11nd, nd)
    
    # Export Result
    return obj_to_rst(
        ndsi, out, sb03.GetGeoTransform(),
        rst_epsg(sb03), noData=nd
    )


def calc_ci_rededge(nir, rededge, out):
    """
    Calculate Chlorophyll IndexRedEdge

    https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=131
    """

    # Open Images
    snir = gdal.Open(nir, gdal.GA_ReadOnly)
    sred = gdal.Open(rededge, gdal.GA_ReadOnly)
    
    # To Array
    nnir = snir.GetRasterBand(1).ReadAsArray().astype(float)
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)

    # Do calculation
    cire = np.where(
        nred == 0, 100,
        (nnir / nred) - 1
    )

    # Place NoData Value
    nd_nir = snir.GetRasterBand(1).GetNoDataValue()
    nd_red = sred.GetRasterBand(1).GetNoDataValue()

    nd_cire = np.amin(cire) - 1

    np.place(cire, nnir==0, nd_cire)
    np.place(cire, nred==0, nd_cire)

    np.place(cire, nnir==nd_nir, nd_cire)
    np.place(cire, nred==nd_red, nd_cire)

    # Export Result
    return obj_to_rst(
        cire, out, snir.GetGeoTransform(),
        rst_epsg(snir), noData=nd_cire
    )


def calc_coloration_idx(red, blue, out):
    """
    Calculate Coloration Index

    https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=11
    """

    # Open Images
    sred  = gdal.Open(red, gdal.GA_ReadOnly)
    sblue = gdal.Open(blue, gdal.GA_ReadOnly)

    # To Array
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)
    nblue = sblue.GetRasterBand(1).ReadAsArray().astype(float)

    # Do calculation
    ci = np.where(nred == 0, 100, (nred - nblue) / nred)

    # Place NoData Value
    nd_red  = sred.GetRasterBand(1).GetNoDataValue()
    nd_blue = sblue.GetRasterBand(1).GetNoDataValue()

    nd_ci = np.amin(ci) - 1

    np.place(ci, nred==0, nd_ci)
    np.place(ci, nblue==0, nd_ci)

    np.place(ci, nred==nd_red, nd_ci)
    np.place(ci, nblue==nd_blue, nd_ci)

    return obj_to_rst(
        ci, out, sred.GetGeoTransform(),
        rst_epsg(sred), noData=nd_ci
    )


def calc_gndvi(nir, green, orst):
    """
    Compute Green Normalized Difference Vegetation
    Index

    https://custom-scripts.sentinel-hub.com/sentinel-2/gndvi/
    """

    # Open Images
    snir = gdal.Open(nir, gdal.GA_ReadOnly)
    sgre = gdal.Open(green, gdal.GA_ReadOnly)
    
    # To Array
    nnir = snir.GetRasterBand(1).ReadAsArray().astype(float)
    ngre = sgre.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    den = nnir + ngre
    gndvi = np.where(
        den == 0, 100,
        (nnir - ngre) / den
    )
    
    # Place NoData Value
    nir_nd = snir.GetRasterBand(1).GetNoDataValue()
    gre_nd = sgre.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(gndvi) - 1

    np.place(gndvi, den == 0, nd)
    
    np.place(gndvi, nnir == nir_nd, nd)
    np.place(gndvi, ngre == gre_nd, nd)

    return obj_to_rst(
        gndvi, orst, snir.GetGeoTransform(),
        rst_epsg(snir), noData=nd
    )


def calc_ndci(b05, b04, orst):
    """
    Compute Normalized Difference Chlorophyll Index

    https://custom-scripts.sentinel-hub.com/sentinel-2/ndci/
    """

    # Open Images
    sb05 = gdal.Open(b05, gdal.GA_ReadOnly)
    sb04 = gdal.Open(b04, gdal.GA_ReadOnly)
    
    # To Array
    nb05 = sb05.GetRasterBand(1).ReadAsArray().astype(float)
    nb04 = sb04.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    den = nb05 + nb04
    ndci = np.where(
        den == 0, 100,
        (nb05 - nb04) / den
    )
    
    # Place NoData Value
    b05nd = sb05.GetRasterBand(1).GetNoDataValue()
    b04nd = sb04.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(ndci) - 1

    np.place(ndci, den == 0, nd)
    
    np.place(ndci, nb05 == b05nd, nd)
    np.place(ndci, nb04 == b04nd, nd)

    return obj_to_rst(
        ndci, orst, sb05.GetGeoTransform(),
        rst_epsg(sb05), noData=nd
    )

