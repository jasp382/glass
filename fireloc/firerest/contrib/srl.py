"""
Serializers related to user contributions
"""

from rest_framework import serializers

from contrib.models import VolunteersContributions
from contrib.models import VolunteersPositionsBackFront, VolunteersPositions

import time


class ContribSrl(serializers.ModelSerializer):
    class Meta:
        model  = VolunteersContributions
        fields = (
            "fid", "pic", "respic", "datehour",
            "usergeom", "dist", "direction",
            "dsun", "directbf", "orie", "beta",
            "gama", "txt", "pnt_name", 
            "fire_name", "cuser", 
            "ugazimute", "gazimute", "gbfazimute",
            "geomc", "geombfc", "place", "fregid",
            "photostatus", "strips",
            "stripgeom", "stripext"
        )


class ContribPositionsSrl(serializers.ModelSerializer):
    class Meta:
        model  = VolunteersPositions
        fields = ("pid", "geom", "azimute", "cid")


class ContribPosistionsBackFrontSrl(serializers.ModelSerializer):
    class Meta:
        model  = VolunteersPositionsBackFront
        fields = ("pid", "geom", "azimute", "cid")


class ContribTimeStamp(serializers.Field):
    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))


class ReadContribLocs(serializers.ModelSerializer):
    geom  = serializers.SerializerMethodField()
    y     = serializers.SerializerMethodField()
    x     = serializers.SerializerMethodField()

    class Meta:
        model  = VolunteersPositions
        fields = (
            "pid", "geom", "azimute", "cid",
            "x", "y"
        )
    
    def get_geom(self, obj):
        """
        Sanitize geometry object
        """
        
        from osgeo         import ogr
        from glass.prj.obj import prj_ogrgeom

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.geom.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        else:
            return obj.geom.wkt
    
    def get_x(self, obj):
        """
        Return X coordinate
        """

        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        epsg = self.context.get("epsg", None)

        g = ogr.CreateGeometryFromWkt(obj.geom.wkt)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(g, 3763, epsg, api='shply')

            g.FlattenTo2D()

        return g.GetX()
    
    def get_y(self, obj):
        """
        Return X coordinate
        """

        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        epsg = self.context.get("epsg", None)

        g = ogr.CreateGeometryFromWkt(obj.geom.wkt)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(g, 3763, epsg, api='shply')

            g.FlattenTo2D()

        return g.GetY()


class ReadContribBfLocs(serializers.ModelSerializer):
    geom  = serializers.SerializerMethodField()

    class Meta:
        model  = VolunteersPositionsBackFront
        fields = ("pid", "geom", "azimute", "cid")
    
    def get_geom(self, obj):
        """
        Sanitize geometry object
        """
        
        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.geom.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        else:
            return obj.geom.wkt


class ReadContrib(serializers.ModelSerializer):
    timestamp = ContribTimeStamp(source="datehour")
    geom      = serializers.SerializerMethodField()
    geombf    = serializers.SerializerMethodField()
    usergeom  = serializers.SerializerMethodField()
    geomc     = serializers.SerializerMethodField()
    geombfc   = serializers.SerializerMethodField()

    class Meta:
        model = VolunteersContributions
        fields = [
            "fid", "pic", "respic", "datehour",
            "usergeom", "dist", "direction",
            "dsun", "directbf", "orie", "beta",
            "gama", "txt", "pnt_name", 
            "fire_name", "cuser",
            "ugazimute", "timestamp", "geom",
            "geombf", "place", "geomc", "geombfc",
            "fregid", "geomc", "geombfc",
            "strips", "photostatus"
        ]
    
    def get_geom(self, obj):
        """
        Return main geometry or not
        """

        is_g = self.context.get("geom", None)

        if not is_g: return None

        geoms = obj.geom.all()

        srl = ReadContribLocs(
            geoms, many=True,
            context=self.context
        )

        return srl.data
    
    def get_geombf(self, obj):
        """
        Return optional position
        """

        is_g = self.context.get("geombf", None)

        if not is_g: return None

        geoms = obj.geombf.all()

        srl = ReadContribBfLocs(
            geoms, many=True,
            context=self.context
        )

        return srl.data
    
    def get_usergeom(self, obj):
        """
        Return main geometry
        """

        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        is_ug = self.context.get('usergeom')
        if not is_ug: return None

        if not obj.usergeom: return None

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.usergeom.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        return obj.usergeom.wkt
    
    def get_geomc(self, obj):
        """
        Return main geometry
        """

        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        if not obj.geomc: return None

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.geomc.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        return obj.geomc.wkt
    
    def get_geombfc(self, obj):
        """
        Return main geometry
        """

        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        if not obj.geombfc: return None

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.geombfc.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        return obj.geombfc.wkt
    
    def get_photo(self, obj):
        """
        Return photo name
        """

        import os
        from firerest.settings import GEOMEDIA_FOLDERS
        from glass.it.pht      import img_to_str

        ispic = self.context.get("photo", None)

        if not ispic: return None

        photos = GEOMEDIA_FOLDERS["CTB_PHOTOS"]
        picname = obj.pic.split('/')[-2]

        photo_str = img_to_str(os.path.join(photos, picname))

        return photo_str

