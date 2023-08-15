"""
Geospatial Reference data serializers
"""

from rest_framework import serializers

from georef.models import Nutsiii, Concelhos, Freguesias, IneBgri
from georef.models import RefGrid, ExtentGeometry, Nutsii, Places


class ExtSrl(serializers.ModelSerializer):
    bounds = serializers.SerializerMethodField()

    class Meta:
        model = ExtentGeometry
        fields = ["id", "geom", "bounds"]

    def get_bounds(self, obj):
        from osgeo import ogr
        from glass.prj.obj import prj_ogrgeom

        g = ogr.CreateGeometryFromWkt(obj.geom.wkt)

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(g, 3763, epsg, api="shply")

        b = ['left', 'right', 'bottom', 'top']
        ext = g.GetEnvelope()

        return {b[i] : ext[i] for i in range(len(b))}


class RefGridSrl(serializers.ModelSerializer):
    class Meta:
        model = RefGrid
        fields = ['gid', "geom", "cellid"]


class NutsiiSrl(serializers.ModelSerializer):
    class Meta:
        model = Nutsii
        fields = ["fid", "code", "name", "geom"]


class NutsSrl(serializers.ModelSerializer):
    class Meta:
        model = Nutsiii
        fields = ["fid", "code", "name", "geom", "nutii"]


class ConcelhosSrl(serializers.ModelSerializer):
    class Meta:
        model = Concelhos
        fields = ["fid", "code", "name", "geom", "nutiii"]


class MunReadSrl(serializers.ModelSerializer):
    geom = serializers.SerializerMethodField("get_geom")

    class Meta:
        model = Concelhos
        fields = ["fid", "code", "name", "geom", "nutiii"]
    
    def get_geom(self, i):
        """
        Return geometry or not
        """

        from osgeo import ogr
        from glass.prj.obj import prj_ogrgeom

        show_geom = self.context.get("showgeom", None)
        epsg      = self.context.get("epsg", None)

        if not show_geom: return None

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                i.geom.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        return i.geom.wkt


class FregSrl(serializers.ModelSerializer):
    class Meta:
        model = Freguesias
        fields = ["fid", "code", "name", "geom", "munid"]


class ReadFregSrl(serializers.ModelSerializer):
    geom = serializers.SerializerMethodField("get_geom")

    class Meta:
        model = Freguesias
        fields = ["fid", "code", "name", "geom", "munid"]
    
    def get_geom(self, i):
        """
        Return geometry or not
        """

        from osgeo import ogr
        from glass.prj.obj import prj_ogrgeom

        show_geom = self.context.get("showgeom", None)
        epsg      = self.context.get("epsg", None)

        if not show_geom: return None

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                i.geom.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        return i.geom.wkt


class BgriSrl(serializers.ModelSerializer):
    class Meta:
        model  = IneBgri
        fields = ["fid", "code", "lugid", "lugname", "geom", "freg"]


class PlacesSrl(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = [
            "fid", "lugid", "lugname", "altname",
            "geom", "freg", "source"
        ]

