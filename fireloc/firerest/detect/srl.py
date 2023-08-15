import time

from rest_framework import serializers

from detect.models import FirelocApproach
from detect.models import FirelocAssessment, FirelocAttr
from detect.models import FirelocAttrValue
from detect.models import PhotoClassification, PhotoClassAttr
from detect.models import PhotoClassAttrValue
from detect.models import SunData

from geovis.srl  import MapFireSrl
from contrib.srl import ContribSrl
from georef.srl  import PlacesSrl, ReadFregSrl, MunReadSrl


class FirelocAttrSrl(serializers.ModelSerializer):
    class Meta:
        model = FirelocAttr
        fields = ['id', 'slug', 'name', "dtype"]


class FlocAttrValSrl(serializers.ModelSerializer):
    slug  = serializers.SerializerMethodField('get_attrslug')
    name  = serializers.SerializerMethodField('get_attrname')
    dtype = serializers.SerializerMethodField('get_attrtype')

    class Meta:
        model = FirelocAttrValue
        fields = [
            'id', 'fattr', 'floc', 
            'value', 'pointgeom', 'polygeom',
            "slug", "name", "dtype"
        ]
    
    def get_attrslug(self, obj):
        return obj.fattr.slug
    
    def get_attrname(self, obj):
        return obj.fattr.name
    
    def get_attrtype(self, obj):
        return obj.fattr.dtype


class PhotoClassAttrSrl(serializers.ModelSerializer):
    class Meta:
        model = PhotoClassAttr
        fields = ['id', 'slug', 'name', "dtype"]


class FirelocApprSrl(serializers.ModelSerializer):
    class Meta:
        model = FirelocApproach
        fields = ['id', 'slug', 'name', "description"]


class FirelocAssesSrl(serializers.ModelSerializer):
    class Meta:
        model = FirelocAssessment
        fields = [
            'id', 'startime', 'endtime', 
            "ctbstart", "ctbend", 
            "aprch", "nearplace",
            "extent", "fregid", "step",
            "prid", "geom"
        ]


class ReadFlocAssesSrl(serializers.ModelSerializer):
    floclyr = MapFireSrl(read_only=True, many=True)
    flocctb = serializers.SerializerMethodField("get_ctb")
    attr    = FlocAttrValSrl(many=True, read_only=True)
    place   = serializers.SerializerMethodField()
    freg    = serializers.SerializerMethodField()
    geom    = serializers.SerializerMethodField()
    extent  = serializers.SerializerMethodField('get_ext')
    cctb    = serializers.SerializerMethodField('count_ctb')
    mun     = serializers.SerializerMethodField()

    class Meta:
        model = FirelocAssessment
        fields = [
            'id', 'startime', 'endtime', 
            "ctbstart", "ctbend", 
            "aprch", "nearplace",
            "extent", "fregid", "step",
            "floclyr", "flocctb", "attr", "place",
            "prid", "geom", "freg", "cctb", "mun"
        ]
    
    def get_geom(self, obj):
        """
        Return main geometry or not
        """

        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        is_g = self.context.get("geom", None)

        if not is_g: return None

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.geom.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()

        return obj.geom.wkt
    
    def get_ext(self, obj):
        """
        Return extent geometry or not
        """

        from osgeo       import ogr
        from glass.prj.obj import prj_ogrgeom

        is_g = self.context.get("extent", None)

        if not is_g: return None

        epsg = self.context.get("epsg", None)

        if epsg and epsg != 3763 and type(epsg) == int:
            g = prj_ogrgeom(ogr.CreateGeometryFromWkt(
                obj.extent.wkt
            ), 3763, epsg, api='shply')

            g.FlattenTo2D()

            return g.ExportToWkt()

        return obj.extent.wkt
    
    def get_place(self, obj):
        if not obj.nearplace: return None

        srl = PlacesSrl(obj.nearplace, many=False)

        return srl.data
    
    def get_freg(self, obj):
        if not obj.fregid: return None

        srl = ReadFregSrl(obj.fregid, many=False, context={
            'showgeom' : None
        })

        return srl.data
    
    def get_mun(self, obj):
        """
        Get Municipio related to the Fireloc
        """

        if not obj.fregid: return None

        srl = MunReadSrl(
            obj.fregid.munid, many=False,
            context={'showgeom' : None}
        )

        return srl.data
    
    def get_ctb(self, obj):
        """
        Get Contributions
        """

        is_ctb = self.context.get("ctb", None)

        if not is_ctb: return None

        ctbs = obj.ctbs.all()

        srl = ContribSrl(ctbs, many=True)

        return srl.data
    
    def count_ctb(self, obj):
        """
        Count contributions
        """

        is_cctb = self.context.get("cctb", None)

        if not is_cctb: return None

        ctbs = obj.ctbs.all()

        return len(ctbs)


class PhotoClassAttrValSrl(serializers.ModelSerializer):
    slug  = serializers.SerializerMethodField('get_attrslug')
    name  = serializers.SerializerMethodField('get_attrname')

    class Meta:
        model = PhotoClassAttrValue
        fields = ['id', 'pcattr', 'photocls', 'value', "slug", "name"]
    
    def get_attrname(self, obj):
        return obj.pcattr.name
    
    def get_attrslug(self, obj):
        return obj.pcattr.slug


class PhotoClassSrl(serializers.ModelSerializer):
    clsattr = PhotoClassAttrValSrl(read_only=True, many=True)

    class Meta:
        model = PhotoClassification
        fields = ['id', 'isfire', 'issmoke', "ctb", "clsattr"]


class ContribTimeStamp(serializers.Field):
    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))

class SunSrl(serializers.ModelSerializer):
    class Meta:
        model = SunData
        fields = [
            "id", "datehour", "ascension", "declination"
        ]

class ReadSunSrl(serializers.ModelSerializer):
    timestamp = ContribTimeStamp(source="datehour")
    class Meta:
        model = SunData
        fields = [
            "id", "datehour", "ascension", "declination",
            "timestamp"
        ]

