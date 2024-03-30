import requests

from glass.cons.sat import con_datahub
from glass.gp.cnv import ext_to_polygon

class APISentinel:
    def get_keycloak(self, username: str, password: str) -> str:
        data = {
            "client_id": "cdse-public",
            "username": username,
            "password": password,
            "grant_type": "password",
        }
        try:
            r = requests.post(
                "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
                data=data,
            )
            r.raise_for_status()
        except Exception as e:
            raise Exception(
                f"Keycloak token creation failed. Reponse from the server was: {r.json()}"
            )
        return r.json()["access_token"]

    def __init__(self):
        cred = con_datahub()
        self.user, self.passw = cred["USER"], cred["PASSWORD"]

        self.token = self.get_keycloak(self.user, self.passw)
    
    def products_query(self, geofile, startdate, enddate, collection):
        """
        Query Sentinel Produtcs
        """

        aoi = ext_to_polygon(geofile, out_srs=4326, outaswkt=True)

        aoi = aoi.replace('POLYGON ', 'POLYGON')
        
        url = (
            "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
            f"$filter=Collection/Name eq '{collection}' and OData.CSC."
            f"Intersects(area=geography'SRID=4326;{aoi}) and ContentDate/"
            f"Start gt {startdate}T00:00:00.000Z and ContentDate/Start lt {enddate}"
            "T00:00:00.000Z"
        )

        print(url)

        json = requests.get(url).json()

        return json

