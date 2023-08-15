
from rest_framework import serializers
from events.models  import RealFireEvents
from events.models  import BurnAreas, Years

from geovis.srl import MapRFireSrl
from georef.srl import ConcelhosSrl, ReadFregSrl

class RealFireEventsSrl(serializers.ModelSerializer):
    class Meta:
        model = RealFireEvents
        fields = (
            "id", "codsgif", "codncco", "tipo", "causa",
            "start", "end", "geom", "name", "fregid", "nearplace",
            "step"
            #"firelyr"
        )

class ReadFireSrl(serializers.ModelSerializer):
    freg = ReadFregSrl(many=True, read_only=True)
    mun = ConcelhosSrl(many=True, read_only=True)
    firelyr = MapRFireSrl(many=True, read_only=True)
    geom = serializers.SerializerMethodField()
    burnedarea = serializers.SerializerMethodField()

    class Meta:
        model = RealFireEvents
        fields = (
            "id", "codsgif", "codncco", "tipo", "causa",
            "start", "end", "geom", "name",
            "firelyr", "burnedarea", "freg", "mun",
            "fregid", "nearplace", "step"
        )
    
    def get_geom(self, obj):
        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        is_geom = self.context.get("geom", None)

        if not is_geom: return None

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.geom.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        else:
            return obj.geom.wkt
    
    def get_burnedarea(self, obj):
        """
        Return burned area in heactares
        """

        is_barea = self.context.get("barea", None)

        if not is_barea: return None

        return round(obj.geom.area / 10000, 2)



class BurnedAreaSrl(serializers.ModelSerializer):
    class Meta:
        model = BurnAreas
        fields = ("id", "geom", "refstart", "refend")     

class YearSrl(serializers.ModelSerializer):
    class Meta:
        model = Years
        fields = ("id", "year")          
