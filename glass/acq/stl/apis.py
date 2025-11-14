import requests
import os

import pandas as pd
import geopandas as gp
import datetime as dt
import threading as th
from shapely.geometry import shape, mapping

from typing import List, Optional, Dict, Any


import time

import threading as th


from glass.prop.ext import get_ext
from glass.prop.prj import get_epsg
from glass.cons.sat import obtain_token, STAC_URL, get_sentinel2_assets, bandsmap, TOKEN_URL, con_datahub
from glass.gp.cnv   import ext_to_polygon
from glass.pys.oss  import fprop
from glass.wt.shp   import df_to_shp

class APISentinel:

    def get_keycloak(self):
        data = {
            "client_id"  : "cdse-public",
            "username"   : self.user,
            "password"   : self.passw,
            "grant_type" : "password",
        }
        try:
            r = requests.post(self.token_url, data=data)
            r.raise_for_status()
        
        except Exception as e:
            raise Exception(
                f"Keycloak token creation failed. Reponse from the server was: {r.json()}"
            )
        return r.json()
    
    def refresh_token(self):
        data = {
            "client_id"     : "cdse-public",
            "refresh_token" : self.reftoken,
            "grant_type"    : "refresh_token"
        }

        try:
            r = requests.post(self.token_url, data=data)

            r.raise_for_status()

        except Exception as e:
            raise Exception(
                f"Keycloak token refresh failed. Reponse from the server was: {r.json()}"
            )
        
        return r.json()
    
    def update_token(self):
        while True:
            if self.stop_token:
                break

            time.sleep(1)
            self.token_life += 1

            if self.token_life > self.expires - 10:
                # We need to update the token
                self.tokendata = self.refresh_token()
                self.reftoken  = self.tokendata['refresh_token']
                self.expires   = self.tokendata['expires_in']

                self.token_life = 1
    
                print(self.token_life)

    
    def close(self):
        self.stop_token = True
        self.token_th.join()

    def __init__(self):
        cred = con_datahub()
        self.user, self.passw = cred["USER"], cred["PASSWORD"]

        self.token_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
        
        self.tokendata = self.get_keycloak()
        self.token     = self.tokendata['access_token']
        self.reftoken  = self.tokendata['refresh_token']
        self.expires   = self.tokendata['expires_in']

        self.token_life = 1
        self.stop_token = None

        self.token_th = th.Thread(target=self.update_token)
        self.token_th.start()
    
    def products_query(self, geofile, date, collection,
                       cloud_cover=None, prodtype=None):
        """
        Query Sentinel Produtcs
        """

        aoi = ext_to_polygon(geofile, out_srs=4326, outaswkt=True)

        aoi = aoi.replace('POLYGON ', 'POLYGON')

        startdate, enddate = date

        ccover = "" if not cloud_cover else (
            " and Attributes/OData.CSC.DoubleAttribute/any("
            "att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value "
            f"le {str(float(cloud_cover))})"
        )

        ptype = "" if not prodtype else (
            " and Attributes/OData.CSC.StringAttribute/any("
            "att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value "
            f"eq '{prodtype}')"
        )
        
        url = (
            "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
            f"$filter=Collection/Name eq '{collection}'{ccover}{ptype} and OData.CSC."
            f"Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/"
            f"Start gt {startdate}T00:00:00.000Z and ContentDate/Start lt {enddate}"
            "T00:00:00.000Z&$expand=Attributes&$top=1000"
        )

        rsp = requests.get(url)

        if rsp.status_code != 200:
            raise ValueError(
                f'Error during URL parsing. Reponse from the server was: {rsp.json()}'
            )
        
        data = rsp.json()

        return data['value']
    
    def to_geodf(self, products):
        """
        Products response to GeoDataFrame
        """

        nprods = []
        for p in products:
            np = {
                'uid'      : p['Id'],
                'name'     : fprop(p['Name'], 'fn'),
                'pubdate'  : p['PublicationDate'],
                'moddata'  : p['ModificationDate'],
                'online'   : p['Online'],
                'imgdate'  : p['ContentDate']['Start'],
                'geometry' : p['Footprint'].split(';')[1][:-1]
            }

            for attr in p['Attributes']:
                np[attr['Name']] = attr['Value']
    
            nprods.append(np)
        
        pdf = pd.DataFrame.from_dict(nprods)

        pdf["geometry"] = gp.GeoSeries.from_wkt(pdf["geometry"], crs="EPSG:4326")

        pdf = gp.GeoDataFrame(pdf, geometry='geometry', crs="EPSG:4326")

        return pdf
    
    def to_shp(self, products, outshp):
        """
        Products to File
        """

        pdf = self.to_geodf(products)

        df_to_shp(pdf, outshp)

        return outshp

    def download(self, img_uid, img_name, out_folder):
        """
        Download Sentinel Image
        """

        oimg = os.path.join(out_folder, f'{img_name}.zip')
        oerro = os.path.join(out_folder, f'{img_name}.txt')

        session = requests.Session()

        session.headers.update({'Authorization' : f'Bearer {self.token}'})

        url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({img_uid})/$value"
        response = session.get(url, allow_redirects=False)

        while response.status_code in (301, 302, 303, 307):
            url = response.headers['Location']
            response = session.get(url, allow_redirects=False)

        file = session.get(url, verify=False, allow_redirects=True)

        if file.status_code != 200:
            with open(oerro, 'wb') as _p:
                _p.write(file.content)
            
            session.close()
            
            return oerro

        with open(oimg, "wb") as p:
            p.write(file.content)
        
        session.close()

        return oimg


class SearchCopernicusStack():
    """
    Searching for Sentinel data
    """

    search_body = None
    token       = None
    items       = []
    assets      = []

    def __init__(self, search_params, assets:list[str]|None=None):
        self.search_body = search_params

        self.token, rsp = obtain_token(totp=None)

        if not assets:
            assets = get_sentinel2_assets()
        
        bndmap = bandsmap()

        for b in assets:
            for k in bndmap:
                if b == bndmap[k]:
                    self.assets.append(k)
                    break
    
    def statres_to_gdf(self, items_):
        """
        Items to GeoDataFrame
        """

        main_cols = ["img_id", "geometry", "collection"]

        prop_cols = {
            'datetime'                         : 'datetime',
            'eo:cloud_cover'                   : 'cloudcover',
            'processing:level'                 : 'proc_level',
            'view:sun_azimuth'                 : 'sunazimuth',
            'statistics.nodata'                : 'nodata', 
            'statistics.dark_area'             : 'dark_area',
            'statistics.vegetation'            : 'vegetation',
            'statistics.thin_cirrus'           : 'thin_cirrus',
            'statistics.cloud_shadow'          : 'cloud_shadow',
            'statistics.unclassified'          : 'unclassified',
            'statistics.not_vegetated'         : 'not_vegy',
            'statistics.high_proba_clouds'     : 'high_proba_clouds',
            'statistics.medium_proba_clouds'   : 'medium_proba_clouds',
            'storage:schemes.cdse-s3.platform' : 'platform'
        }

        assets_cols = {'Product.href' : 'downurl'}

        dfcols = main_cols + list(prop_cols.values()) + \
            list(assets_cols.values())
        
        if not len(items_):
            gdf = gp.GeoDataFrame(
                columns=dfcols,
                geometry="geometry", crs="EPSG:4326"
            )

            return gdf
        
        # Create DataFrame
        gdf = pd.DataFrame(items_, columns=list(items_[0].keys()))

        df_prop   = pd.json_normalize(gdf["properties"])
        df_assets = pd.json_normalize(gdf["assets"])

        gdf["geometry"] = gdf.geometry.apply(shape)

        dc = ["type", "bbox", "links", "stac_extensions", "stac_version", "properties", "assets"]
        gdf.drop(dc, axis=1, inplace=True)
        gdf.rename(columns={'id' : 'img_id'}, inplace=True)

        # Re-define prop/assets columns and join
        each_df      = [df_prop, df_assets]
        cols_each_df = [prop_cols, assets_cols]
        for i in range(len(each_df)):
            _dc = [c for c in each_df[i].columns.values if c not in cols_each_df[i]]
            each_df[i].drop(_dc, axis=1, inplace=True)
            each_df[i].rename(columns=cols_each_df[i], inplace=True)

            gdf = gdf.merge(each_df[i], how='left', left_index=True, right_index=True)
        
        # Create tile id column
        tiledf = gdf.img_id.str.split('_', n=-1, expand=True)

        tiledf.rename(columns={5: 'tileid'}, inplace=True)
        tiledf.drop([c for c in tiledf.columns.values if c != 'tileid'], axis=1, inplace=True)

        gdf = gdf.merge(tiledf, how='left', left_index=True, right_index=True)
        
        gdf = gp.GeoDataFrame(gdf, geometry="geometry", crs="EPSG:4326")

        # convert datetime string to pandas datetime
        gdf["datetime"] = gdf["datetime"].map(lambda v: v and (v.replace("Z", "") if isinstance(v, str) else v))
        gdf["datetime"] = gdf["datetime"].map(lambda v: (v and (dt.datetime.fromisoformat(v) if isinstance(v,str) else v)))

        return gdf
    
    def stac_search(self, page_limit: int = 100, rgeodf:bool=False) -> List[Dict[str, Any]]:
        """
        Search for images
        """

        headers = {"Content-Type": "application/json"}

        if not self.token:
            raise ValueError("Token is not available")
        
        headers["Authorization"] = f'Bearer {self.token}'

        url = STAC_URL.rstrip("/") + '/search'

        items = []

        body = dict(self.search_body)

        body["limit"] = page_limit
        tstlinks = []

        while body:
            r = requests.post(url, headers=headers, json=body, timeout=60)
            
            if r.status_code != 201 and r.status_code != 200:
                print(r.status_code)
                print(r.text)
            
            r.raise_for_status()

            js = r.json()

            if "features" in js:
                items.extend(js["features"])
            
            else:
                items.extend(js.get("items", []))
            
            # Find next link
            tstlinks.append(js.get("links", []))
            next_body = None
            for link in js.get("links", []):
                if link.get("rel") == "next":
                    next_body = link.get("body")
                    break
            
            if next_body:
                body = next_body
            
            else:
                body = None

        if rgeodf:
            _gdf = self.statres_to_gdf(items)

            self.items = _gdf
        
            return _gdf
        
        else:
            self.items = items

            return items
    
    def items_to_shp(self, outfile:str, osrs:int|None=None, olyr:str|None=None):
        """
        Items to GeoPackage
        """

        from glass.wt.shp import df_to_shp
        from glass.prj.obj import df_prj

        if osrs and osrs != 4326:
            gdf = df_prj(self.items, osrs)
        
        else:
            gdf = self.items
        
        df_to_shp(gdf, outfile, layername=olyr)

        return outfile


class TokenManager:
    """
    Garante access_token válido, faz refresh automático usando refresh_token quando necessário.
    Thread-safe: usa Lock para evitar refresh concorrente.
    """

    _access_token = None

    def __init__(self, totp: Optional[str] = None):
        
        
        tokenjs, rsp = obtain_token(totp=None, justToken=False)
        self._access_token = tokenjs["access_token"]
        #self._access_token = 'primeiro_token'
        self.token_url = TOKEN_URL
        self._refresh_token = tokenjs["refresh_token"]
        self._expires_in = tokenjs["expires_in"]
        #self._expires_in = 70
        self.totp = totp
        
        self.token_life = 1
        self.stop_token = None

        self.token_th = th.Thread(target=self.update_token)
        self.token_th.start()
    
    def update_token(self):
        while True:
            if self.stop_token:
                break

            time.sleep(1)

            self.token_life += 1

            if self.token_life > self._expires_in - 60:
                # We need to update token
                self.refresh_token()
                #self._access_token = 'segundo'

                self.token_file = 1
    
    def close(self):
        self.stop_token = True
        self.token_th.join()

    def has_token(self) -> bool:
        return self._access_token is not None

    def force_refresh(self) -> Optional[str]:
        """Force a refresh attempt (refresh_token -> password grant)."""
        return self.get_token(force_refresh=True)

    def refresh_token(self) -> bool:
        """Use refresh_token to get a new access_token."""
        if not self._refresh_token:
            return False
        try:
            data = {
                "client_id": "cdse-public",
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token
            }
            r = requests.post(self.token_url, data=data, timeout=30)
            # if server returns 400/401 etc -> refresh failed
            if r.status_code != 200:
                # clear refresh_token to avoid repeated failing attempts
                print("Refresh token falhou (status {}).".format(r.status_code))
                self._refresh_token = None
                return False
            j = r.json()
            self._access_token = j.get("access_token")
            # sometimes new refresh_token is returned; update it
            self._refresh_token = j.get("refresh_token", self._refresh_token)
            
            self._expires_in = j.get("expires_in", 600)
            print(f"Refresh token bem-sucedido; novo access token válido por ~{str(self._expires_in)}s")
            return True
        except Exception as e:
            print("Excepção durante refresh_token:", e)
            self._refresh_token = None
            return False
    
    def get_token(self):
        return self._access_token


def search_images_for_multipledatetimes(bboxfile, dates, collection, max_cloud, outfile):
    """

    """

    # montar corpo da pesquisa STAC
    bbox_ = get_ext(bboxfile, oepsg=4326)

    bbox = (bbox_[0], bbox_[2], bbox_[1], bbox_[3])

    epsg = get_epsg(bboxfile)

    search_body = {
        "collections": [collection],
        "bbox": list(bbox),
        "query": {
            "eo:cloud_cover": {"lte": max_cloud}
        }
    }

    for k in dates:
        search_body["datetime"] = dates[k]

        search = SearchCopernicusStack(search_body)

        items = search.stac_search(page_limit=500, rgeodf=True)

        search.items_to_shp(outfile, osrs=epsg, olyr=k)
    
    return outfile

