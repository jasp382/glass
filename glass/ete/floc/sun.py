"""
Sun declination related
"""

from firegis.api import get_headers
import requests as rq
import pandas as pd

def get_declination(ano, mes, dia):
    url= (
        "https://midcdmz.nrel.gov/apps/spa.pl?"
        f"syear={ano}&smonth={mes}&sday={dia}"
        f"&eyear={ano}&emonth={mes}&eday={dia}"
        f"&step=1&stepunit=1"
        f"&otype=0&hr=0&min=0&sec=0&"
        f"latitude=0.0&longitude=0.0&timezone=0.0&elev=100.0&"
        f"press=835&temp=10&dut1=0.0&deltat=64.797&"
        f"refract=0.0&field=30&field=31"
    )
    
    out = None
    
    try:
        r = rq.get(url)
    except:
        out = {"status" : -1}
    
    if not out:
        try:
            d = r.text
            
            out = {
                "status" : 1,
                "text"   : d,
                "http"   : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "http"   : r.status_code
            }
    
    return out


def get_declination_asdf(ano, mes, dia):
    """
    Return sun declination value
    """

    rsun = get_declination(ano,mes, dia)

    if rsun["status"] <= 0 or rsun["http"] != 200:
        rsun["description"] = "Error when requesting sun data"

        raise ValueError(str(rsun))
    
    cols = ['date', 'time', 'ascension', 'declination']

    cc = rsun["text"].split('\n')
    
    # To df
    df = pd.DataFrame(cc[1:-1], columns=['data'])
    
    # One column to several
    df[cols] = df['data'].str.split(',', -1, expand=True)

    # Get datetime column
    df['datehour'] = df["date"] + ' ' + df["time"]
    
    df['datehour'] = pd.to_datetime(df['datehour'], format='%m/%d/%Y %H:%M:%S')
    
    df['datehour'] = df["datehour"].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    df["timezone"] = 'UTC'

    df['declination'] = df["declination"].astype(float)
    df['ascension']   = df["ascension"].astype(float)
    
    df.drop(['data', 'date', 'time'], axis=1, inplace=True)
    
    return df


def calc_sun_azimute(df, lon, lat, datehour, ascension=None, declination=None, all_fields=None):
    """
    Return Sun Azimute

    data should be something like this:
    data = [
        #Longitude, latitude, datetime str
        [-11.3866666666667, 37.2097222222222, '2021-01-01 12:10:15'],
        [11.3866666666667, 37.8430555555556, '2021-01-01 12:10:15'],
        [-11.8366666666667, -37.2097222222222, '2021-01-01 12:10:15'],
        [11.8366666666667, -37.2097222222222, '2021-01-01 12:10:15'],
    ]  
    """

    import math
    import numpy as np
    import geopandas as gp

    from firegis.api.sundata import get_sun_decl_as

    ncols = []

    if type(df) != pd.DataFrame and type(df) != gp.GeoDataFrame:
        cols = [lon, lat, datehour]

        if ascension and declination:
            cols.extend([ascension, declination])
        
        df = pd.DataFrame(df, columns=cols)

    # Sanitize DatetimeData - Seconds to zero
    df[datehour] = pd.to_datetime(df[datehour], format='%Y-%m-%d %H:%M:%S')

    df['yy']   = df[datehour].dt.year
    df['mm']   = df[datehour].dt.month
    df['dd']   = df[datehour].dt.day
    df['hr']   = df[datehour].dt.hour
    df['minn'] = df[datehour].dt.minute
    df['sec']  = 0

    df["datestr"] = df[datehour].dt.strftime('%Y-%m-%d-%H-%M')
    df["datestr"] = df["datestr"] + '-00'

    ncols.extend(['yy', 'mm', 'dd', 'hr', 'minn', 'sec', 'datestr'])

    # Get Juliana Date
    # ----------------------------------------------------------- #
    df['yyj'] = np.where(
        (df.mm == 1) | (df.mm == 2),
        df.yy - 1, df.yy
    )

    df['mmj'] = np.where(
        (df.mm == 1) | (df.mm == 2),
        df.mm + 12, df.mm
    )

    #df['dj'] = np.where((df.yy == 1582) & (df.mm < 10), 0, 0)
    df['dj'] = 0

    df['dj'] = np.where(
        (df.yyj == 1582) & (df.mmj == 10) & (df.dd < 4),
        -2, df.dj
    )

    df['dj'] = np.where(
        (df.yyj == 1582) & (df.mmj == 10) & (df.dd > 15),
        np.fix(df.yyj / 400) - np.fix(df.yyj / 100), df.dj
    )

    df['dj'] = np.where(
        (df.yyj == 1582) & (df.mmj > 10), 
        np.trunc(df.yyj / 400.0) - np.trunc(df.yyj / 100.0), df.dj
    )

    df['dj'] = np.where((df.yyj < 1582), 0, df.dj)
    df['dj'] = np.where(
        (df.yyj > 1582), 
        np.trunc(df.yyj / 400.0) - np.trunc(df.yyj / 100.0),
        df.dj
    )
    df['dj'] = np.trunc(
        365.25 * df.yyj
    ) + np.trunc(
        30.6001 * (df.mmj + 1)
    ) + df.dj + 1720996.5 + df.dd

    df["timee"] = df.hr + df.minn / 60 + df.sec / 3600

    ncols.extend(['yyj', 'mmj', 'dj', 'timee'])

    # ----------------------------------------------------------- #

    # Aberracao diurna
    # ----------------------------------------------------------- #
    Rt_lat = 6378000 * np.cos(abs(df[lat]) * np.pi/180.0)
    v_lat = (2*np.pi*Rt_lat) / (24 * 3600)
    df['Ad_rot'] = np.arcsin((v_lat / 299792458)) * 180.0 / np.pi
    df['Ad_tot'] = df['Ad_rot']

    ncols.extend(['Ad_rot', 'Ad_tot'])

    # ----------------------------------------------------------- #

    # Obliquidade Eliptica
    # ----------------------------------------------------------- #
    oe = 23 + (26 /60.0) + (14 / 3600.0)

    # paralaxe geocentrica
    # ----------------------------------------------------------- #
    dist_star = 149600000.0;
    pg = 6378.0 / dist_star; 
    pg = math.asin(pg) * 180.0 / math.pi

    # ----------------------------------------------------------- #

    # Sun ascension and sun declination
    # ----------------------------------------------------------- #
    def get_sundata(row):
        rsd = get_sun_decl_as(token, datehour=row.datestr)
    
        sdata = rsd['json']
    
        row['ar']  = sdata[0]['ascension']
        row['dec'] = sdata[0]['declination']
    
        return row
    
    if not ascension or not declination:
        hout = get_headers()

        if hout["status"] <= 0 or hout['http'] != 201:
            # So
            hout["description"] = "Error when requesting token"

            return 0, None, hout

        token = hout["json"]
    
        df = df.apply(lambda x: get_sundata(x), axis=1)
        df['ar']  = df.ar.astype(float)
        df['dec'] = df.dec.astype(float)
    
    else:
        df["ar"]  = df[ascension].astype(float)
        df["dec"] = df[declination].astype(float)
    # ----------------------------------------------------------- #

    # Angulo Horario
    # ----------------------------------------------------------- #
    tu = (df.dj - 2451545) / 36525
    TSMG_0hTu = 6 + (41/60) + (50.54841/3600) + \
        ((8640184.812866/3600)*tu)+((0.093104/3600)*tu*tu)\
            -((0.0000062/3600)*tu*tu*tu)
    
    TSMG_GMST = TSMG_0hTu

    delta_TSM = (24*df.timee) / (23+(56/60)+(4.091/3600))

    TSMG = TSMG_GMST + delta_TSM

    TSM = TSMG + (df[lon] * 24 / 360)

    # Equacao equinocios
    # ----------------------------------------------------------- #
    delta_F = (-17.200 / 3600) * np.sin((125.045 - 1934.136*tu) * np.pi / 180.0)

    EqEq = delta_F * np.cos(oe*np.pi/180.0)

    TS = TSM + (EqEq * (24.0 / 360))
    TS_GSM = TS%24

    # Altura
    # ----------------------------------------------------------- #
    H = TS_GSM - df.ar

    df["hh"] = np.where(H < 0, 24 + H, H)

    df["h"] = np.arcsin(np.cos((90-df[lat])*np.pi/180.0)* \
        np.cos((90-df.dec)*np.pi/180.0)+np.sin((90-df[lat])*np.pi/180.0)\
            *np.sin((90-df.dec)*np.pi/180.0)*np.cos(\
                (df.hh*360.0/24)*np.pi/180.0)) * 180.0 / np.pi
    
    ncols.extend(['hh', 'h'])
    # ----------------------------------------------------------- #
    
    # Azimute
    # ----------------------------------------------------------- #
    df['a'] = np.arccos((np.cos((90-df.dec)*np.pi/180.0)-\
        np.cos((90-df[lat])*np.pi/180.0)*np.cos((90-df.h)*np.pi/180.0))/\
            (np.sin((90-df[lat])*np.pi/180.0)*np.sin((90-df.h)\
                *np.pi/180.0)))*180.0/np.pi

    # Azimute em graus
    df['ac'] = np.where(df.hh < 12, df.a, 360 - df.a)

    # Azimute Stellarium
    df['as'] = np.where(df.hh < 12, 360 - df.a, df.a)

    ncols.append('a')
    # ----------------------------------------------------------- #
    
    # Distancia Zenital
    # ----------------------------------------------------------- #
    df['dz']   = 90 - df.h
    df['dz_g'] = np.trunc(df.dz)
    df["dz_m"] = np.absolute(np.trunc((df.dz - df.dz_g)*60))
    df["dz_s"] = (((np.absolute(df.dz)-np.absolute(df.dz_g)) * 60) \
        - df.dz_m)*60
    
    ncols.extend(['dz', 'dz_g', 'dz_m', 'dz_s'])
    # ----------------------------------------------------------- #
    
    # Apply corrections
    # ----------------------------------------------------------- #
    elevacaoSolar = df.h
    hgraus        = df.h * np.pi/180
    refAtmosf     = 0  
    
    df['hr'] = np.where(df.h >= 0, refAtmosf, df.h)
    df['hr'] = np.where(
        (df.h >= 0) & (elevacaoSolar >= 85) & (elevacaoSolar <= 90),
        0, df.hr
    )
    df['hr'] = np.where(
        (df.h>=0)&(elevacaoSolar<85)&(elevacaoSolar>=5),
        1/3600.0*(58.1/np.tan(df.h)-0.07/np.power(np.tan(df.h), 3) \
            + 0.000086/np.power(np.tan(df.h),5)), df.hr
        )
    
    df['hr'] = np.where(
        (df.h>=0)&(elevacaoSolar<5)&(elevacaoSolar>=-0.575),
        1/3600.0*(1735-518.2*df.h+103.4*np.power(df.h, 2)- 12.79*np.power(df.h, 3) + \
            0.711*np.power(df.h, 4)), df.hr
    )
    
    df['hr'] = np.where(
        (df.h>=0)&(elevacaoSolar<-0.575),
        1 / 3600.0 * (-20.774 / np.tan(df.h)), df.hr
    )

    df['hcorr'] = df.hr - pg

    # Azimute corr
    df['Accorr'] = np.where(df.h >= 0, df.ac - df.Ad_tot, df.ac)

    # Azimute Stellarium corr
    df['Ascorr'] = np.where(df.h >= 0, df['as'] - df.Ad_tot, df['as'])

    ncols.extend(["hr", "hcorr"])

    if not all_fields:
        df.drop(ncols, axis=1, inplace=True)

    return 1, df, None


def sunazimute_to_ctb(token, df, geom, dhour, _dhour, dstr):
    """
    For each contribution, get the Sun Azimute
    """

    from firegis.api.sundata import get_sun_decl_as
    from glass.it.pd import obj_to_geodf

    # To GeoDataFrame
    df = obj_to_geodf(df, geom, '4326')

    # Get x, y values
    df['lat'], df['lng'] = df[geom].y, df[geom].x

    # Sanitize datehour field and create datestr to query API
    df[dhour] = pd.to_datetime(
        df[dhour], format='%Y-%m-%d %H:%M:%S'
    )
    df[dstr] = df[dhour].dt.strftime('%Y-%m-%d-%H-%M')
    df[dstr] = df[dstr] + '-00'
    df[dhour] = pd.to_datetime(df[dstr], format='%Y-%m-%d-%H-%M-%S')

    min_time = df[dhour].min()
    min_time = min_time.strftime('%Y-%m-%d-%H-%M-%S')
    max_time = df[dhour].max()
    max_time = max_time.strftime('%Y-%m-%d-%H-%M-%S')

    # Get Declination and ascension
    dasr = get_sun_decl_as(token, datehour=min_time, endtime=max_time)

    if dasr["status"] <= 0 or dasr["http"] != 200:
        return 0, None, dasr
    
    das = pd.DataFrame(dasr['json'])

    das[_dhour] = pd.to_datetime(das.timestamp, unit='s')
    das[_dhour] = das[_dhour].dt.strftime('%Y-%m-%d %H:%M:%S')

    das.drop(["datehour", "id", "timestamp"], axis=1, inplace=True)

    # Join with main dataframe
    df[dstr] = df[dhour].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.merge(das, how='left', left_on=dstr, right_on=_dhour)

    cols = [dstr, _dhour]
            
    df.drop(cols, axis=1, inplace=True)

    __, df, _ = calc_sun_azimute(
        df, 'lng', 'lat', dhour,
        ascension="ascension", declination="declination"
    )

    return 1, df, None
    
