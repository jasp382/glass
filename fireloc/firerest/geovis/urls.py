"""
Geo Visualisation URLS Routing
"""

from django.urls import path

from geovis.views         import ManGLayers, ManGLayer, RetrieveGLayers
from geovis.views.charts  import ManGeoCharts, ManGeoChart
from geovis.views.charts  import ManChartData
from geovis.views.fireev  import ManFireLyrs, ManFireLyr
from geovis.views.fireev  import ManRFireLegend, RFireLegEntrance
from geovis.views.leg     import ManLegend, LegEntrance
from geovis.views.rel     import GLayersUsers
from geovis.views.flocev  import ManFLocAssessWS, ManFLocAssessLyr
from geovis.views.flocev  import ManFireLegend, FireMapLegEntrance
from geovis.views.contrib import ManSingleCtbLayers, ManSingleCtbLayer
from geovis.views.cluster import ManClusterLayers, ManClusterLayer
from geovis.views.perm    import ManPermLayer, ManPermLayers


urlpatterns = [
    # Geoportal Layers
    path(
        'geoportal-layers/', ManGLayers.as_view(),
        name='manage-geoportal-layers'
    ),
    path(
        'geoportal-layer/<str:lyr>/', ManGLayer.as_view(),
        name='manage-geoportal-layer'
    ),
    path(
        'glayers-uu/', RetrieveGLayers.as_view(),
        name='list-geolayers-uu'
    ),

    # Cluster Layers
    path(
        'cluster-layers/', ManClusterLayers.as_view(),
        name='manage-cluster-layers'
    ),
    path(
        'cluster-layer/<str:lyr>/', ManClusterLayer.as_view(),
        name='manage-cluster-layer'
    ),

    # Permanent Layers
    path(
        'marker-layers/', ManPermLayers.as_view(),
        name='marker-cluster-layers'
    ),
    path(
        'marker-layer/<str:lyr>/', ManPermLayer.as_view(),
        name='marker-cluster-layer'
    ),

    # Fireloc Layers
    path(
        'fireloc-layers/', ManFLocAssessWS.as_view(),
        name='manage-fireloc-layers'
    ),

    path(
        'fireloc-layer/<int:lyr>/', ManFLocAssessLyr.as_view(),
        name='manage-fireloc-layer'
    ),

    # Real Fire Layers
    path(
        "fire-events-layers/", ManFireLyrs.as_view(),
        name="manage-fireevents-layers"
    ),
    path(
        "fire-event-layer/<int:lyr>/", ManFireLyr.as_view(),
        name="manage-fireevent-layer"
    ),

    # Layers Legends
    path(
        'layers-legend/', ManLegend.as_view(),
        name='manage-layers-legend'
    ),

    # Layer Entrance
    path(
        'legend-i/<int:legid>/', LegEntrance.as_view(),
        name='manage-legend-entrance'
    ),

    # Fire Maps Legend
    path(
        'firemaps-legend/', ManFireLegend.as_view(),
        name='manage-firemaps-legends'
    ),

    path(
        'firemap-legend/<int:legid>/', FireMapLegEntrance.as_view(),
        name='manage-firemap-legend'
    ),

    # Fire Events Legend
    path(
        'fire-events-legend/', ManRFireLegend.as_view(),
        name="manage-fireev-legend"
    ),
    path(
        'fire-event-leg/<int:legid>/', RFireLegEntrance.as_view(),
        name="manage-fireev-legi"
    ),

    # Relationship User Groups and Geoportal Layers
    path(
        'layers-groups/<str:group>/', GLayersUsers.as_view(),
        name='rel-layer-groups'
    ),

    # GeoCharts and their series
    path(
        'geo-charts/', ManGeoCharts.as_view(),
        name='geo-charts'
    ),
    path(
        'geo-chart/<str:chartid>/', ManGeoChart.as_view(),
        name='geo-chart'
    ),
    path(
        'geo-chart-data/<str:chartid>/<str:seriesid>/', ManChartData.as_view(),
        name='geo-chart-data'
    ),

    # Single Contrib Layers
    path(
        'single-ctb-layers/', ManSingleCtbLayers.as_view(),
        name='single-contribution-layers'
    ),

    path(
        'single-ctb-layer/<str:lyr>/', ManSingleCtbLayer.as_view(),
        name='single-contribution-layer'
    )
]