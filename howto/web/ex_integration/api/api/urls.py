"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from layers.views import ManLayers, ManLayer
from geoms.views import ReceiveLayerFiles, ManGeoms, ManGeom
from gserver.views import GeoServerLayers, GeoServerLayersStyle
from gserver.views import get_extent, get_wfs, get_wms
from gserver.views import get_featinfo, get_legend_ml

urlpatterns = [
    path('admin/', admin.site.urls),

    path('layers/', ManLayers.as_view()),

    path('layer/<int:lid>/', ManLayer.as_view()),

    path('geoms/<int:lid>/', ManGeoms.as_view()),

    path('geom/<int:fid>/', ManGeom.as_view()),

    path('layerdata/<int:lyr>/', ReceiveLayerFiles.as_view()),

    path('geoserver/addlayer/<int:lid>/', GeoServerLayers.as_view()),
    path('geoserver/wfs/<str:work>/<str:lyr>/', get_wfs, name='api_wfs'),
    path('geoserver/extent/<str:work>/<str:lyr>/', get_extent, name='api-extent'),
    path('geoserver/featinfo/<str:work>/<str:lyr>/', get_featinfo, name='api-featinfo'),
    path('geoserver/wms/<str:work>/', get_wms, name='api-wms'),
    path('geoserver/multileg/<str:work>/', get_legend_ml, name='get_legend_ml'),
    path('geoserver/style/<int:lid>/', GeoServerLayersStyle.as_view())

]
