"""tstleaflet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from leaf.views import map_view
from leaf.views import get_extent
from leaf.views import get_wfs
from leaf.views import get_featinfo
from leaf.views import get_wms
from leaf.views import get_legend_ml

urlpatterns = [
    path('', map_view, name='leaflet-map'),
    path('api/wfs/<str:work>/<str:lyr>/', get_wfs, name='api_wfs'),
    path('api/extent/<str:work>/<str:lyr>/', get_extent, name='api-extent'),
    path('api/featinfo/<str:work>/<str:lyr>/', get_featinfo, name='api-featinfo'),
    path('api/wms/<str:work>/', get_wms, name='api-wms'),
    path('api/multileg/<str:work>/', get_legend_ml, name='get_legend_ml'),
    path('admin/', admin.site.urls),
]
