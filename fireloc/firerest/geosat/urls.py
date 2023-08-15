"""
Satellite data management
"""


from django.urls import path

from geosat.views.tiles import ManSentinelTiles, ManSentinelTile
from geosat.views.img   import ManSentinelImgs, ManSentinelImg

urlpatterns = [
    path(
        'sentinel-tiles/', ManSentinelTiles.as_view(),
        name='manage-sentinel-tiles'
    ),

    path(
        'sentinel-tile/<str:cellid>/', ManSentinelTile.as_view(),
        name='manage-sentinel-tile'
    ),

    path(
        'sentinel-imgs/', ManSentinelImgs.as_view(),
        name='manage-sentinel-images'
    ),

    path(
        'sentinel-img/<str:imgid>/', ManSentinelImg.as_view(),
        name='manage-sentinel-image'
    )
]