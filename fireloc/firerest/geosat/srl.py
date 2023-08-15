"""
Sentinel related serializers
"""


from rest_framework import serializers

from geosat.models import SentinelTiles
from geosat.models import SentinelImages


class SentinelImgSrl(serializers.ModelSerializer):
    class Meta:
        model = SentinelImages
        fields = (
            'id', 'title', 'link', 'summary',
            'ondemand', 'beginposition', 'endposition', 'ingestiondate',
            'generationdate', 'orbitnumber', 'relativeorbitnumber',
            'vegetationpercentage', 'notvegetatedpercentage',
            'waterpercentage', 'unclassifiedpercentage',
            'mediumprobacloudspercentage', 'highprobacloudspercentage',
            'snowicepercentage', 'cloudcoverpercentage',
            'illuminationazimuthangle', 'illuminationzenithangle',
            'level1cpdiidentifier', 'format', 'processingbaseline',
            'platformname', 'filename', 'instrumentname',
            'instrumentshortname', 'size', 's2datatakeid', 'producttype',
            'platformidentifier', 'orbitdirection', 'platformserialidentifier',
            'processinglevel', 'identifier', 'datastripidentifier',
            'granuleidentifier', 'uuid', 'geometry', 'tileid',
            "isdownload"
        )


class SentinelTileSrl(serializers.ModelSerializer):
    class Meta:
        model = SentinelTiles
        fields = ("id", "slugid", "geom")


class StlTileReadSrl(serializers.ModelSerializer):
    lastimg = serializers.SerializerMethodField()

    class Meta:
        model = SentinelTiles
        fields = ("id", "slugid", "geom", "lastimg")
    
    def get_geom(self, obj):
        """
        Sanitize geometry object
        """
        
        from firerest.settings import PRJ_EPSG
        from osgeo             import ogr
        from glass.prj.obj import prj_ogrgeom

        epsg = self.context.get("epsg", None)
        rgeom = self.context.get("showgeom", None)

        if not rgeom: return None

        if epsg and epsg != PRJ_EPSG and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.geom.wkt
            ), PRJ_EPSG, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()
        
        else:
            return obj.geom.wkt
    
    def get_lastimg(self, obj):
        """
        Get most recent Image for this cell
        """

        islastimg = self.context.get("lastimg", None)

        if not islastimg: return None
        
        else:
            img = SentinelImages.objects.filter(
                cellid=obj.id
            ).order_by('-ingestiondate')

            if not len(img): return None
        
            img = img[0]

            srl = SentinelImgSrl(img)

            return srl.data

