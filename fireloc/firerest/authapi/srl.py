"""
AUTH API Serializers
"""

from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from authapi.models import UserCodes, UserAttr, UserAttrValue
from authapi.models import Organizations

from geovis.srl import MapLayersSrl

class GroupsSrl(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    layers = serializers.SerializerMethodField("get_lyr")

    class Meta:
        model = Group
        fields = ("id", "name", "users", "layers")
    
    def create(self, vd):
        """
        Create new group
        """

        return Group.objects.create(
            name=vd.get('name')
        )
    
    def get_users(self, obj):
        """
        Return users if requested
        """

        is_users = self.context.get("users", None)

        if not is_users: return None

        us = obj.user_set.all()

        srl = UserSrl(us, many=True)

        return srl.data
    
    def get_lyr(self, obj):
        """
        Return layers if requested
        """

        islyr = self.context.get("layers", None)

        if not islyr: return None

        lyrs = obj.maplayers.all()

        srl = MapLayersSrl(lyrs, many=True)

        return srl.data


class UserAttrSrl(serializers.ModelSerializer):
    class Meta:
        model = UserAttr
        fields = ['id', 'slug', 'name', "atype"]
   

class UserAttrValueSrl(serializers.ModelSerializer):
    attrname = serializers.SerializerMethodField('get_attrname')
    attrslug = serializers.SerializerMethodField('get_attrslug')

    class Meta:
        model = UserAttrValue
        fields = [
            'id', 'attr', 'user', 'value', 'attrname',
            "attrslug"
        ]
    
    def get_attrname(self, obj):
        return obj.attr.name
    
    def get_attrslug(self, obj):
        return obj.attr.slug


class UserCodeSrl(serializers.ModelSerializer):
    class Meta:
        model = UserCodes
        fields = ("user_id", "token","confirmation")


class UserSrl(serializers.ModelSerializer):
    token  = UserCodeSrl(many=True, read_only=True)
    #groups = GroupsSrl(many=True, read_only=True)
    usgroup = serializers.SerializerMethodField("get_group")
    attr   = UserAttrValueSrl(many=True, read_only=True)
    active = serializers.SerializerMethodField('is_active')

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "password",
            "first_name", "last_name",
            "token", "usgroup", "attr", "active"
        )
    
    def create(self, vd):
        """
        Create new User
        """

        import datetime as dt
        import pytz

        tz   = pytz.timezone('UTC')
        _now = dt.datetime.utcnow().replace(microsecond=0)
        now  = tz.localize(_now)

        return User.objects.create_user(
            username     = vd["username"],
            email        = vd["email"],
            password     = vd["password"],
            is_superuser = False,
            first_name   = vd["first_name"],
            last_name    = vd["last_name"],
            is_staff     = False,
            is_active    = True,
            last_login   = now,
            date_joined  = now
        )
    
    def is_active(self, obj):
        """
        Check if the user is active or not
        """

        ustoken = obj.token.filter(confirmation=True)

        return True if ustoken else False
    
    def get_group(self, obj):
        """
        Return User Group
        """

        groups = obj.groups.all()

        if not groups: return None

        group = groups[0]

        srl = GroupsSrl(group)

        return srl.data


class OrgSrl(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "alias", "name", "address",
            "city", "state", "postal", "country",
            "countryi", "phone", "email"
        )

