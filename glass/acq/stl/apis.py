import requests
import os

import pandas as pd
import geopandas as gp

import time

import threading as th

from glass.cons.sat import con_datahub
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

