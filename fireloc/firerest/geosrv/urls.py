"""
Spatial Data Infrastructure URLS Routing
"""

from django.urls import path

from geosrv.views.ws import GeoServerWorkspaces, GeoServerWorkspace
from geosrv.views.st import GeoServerStores, GeoServerStore
from geosrv.views.lyr import GeoServerLayers, GeoServerLayer
from geosrv.views.styles import GeoServerStyles, GeoServerStyle

from geosrv.views.parse import get_wms, GetWFS


urlpatterns = [
    # GeoServer Workspaces
    path(
        'workspaces/', GeoServerWorkspaces.as_view(),
        name='geoserver-workspaces'
    ),

    path(
        'workspace/<str:ws>/', GeoServerWorkspace.as_view(),
        name='geoserver-workspace'
    ),

    # GeoServer Stores
    path(
        '<str:ws>/stores/', GeoServerStores.as_view(),
        name='geoserver-stores'
    ),

    path(
        '<str:ws>/store/<str:st>/', GeoServerStore.as_view(),
        name='geoserver-store'
    ),

    # GeoServer Layers
    path(
        'layers/', GeoServerLayers.as_view(),
        name='geoserver-layers'
    ),

    path(
        'layer/<str:lyr>/', GeoServerLayer.as_view(),
        name='geoserver-layer'
    ),

    # GeoServer Styles
    path(
        'styles/', GeoServerStyles.as_view(),
        name='geoserver-styles'
    ),

    path(
        'style/<str:style>/', GeoServerStyle.as_view(),
        name='geoserver-style'
    ),

    # Parse services
    # Parse WMS
    path('wms/<str:work>/', get_wms, name='geoserver-wms'),
    # Parse WFS
    path(
        'wfs/<str:work>/<str:lyr>/', GetWFS.as_view(),
        name='geoserver-wfs'
    )
]