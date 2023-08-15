"""firerest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls    import path, include, re_path

from drf_yasg.views import get_schema_view
from drf_yasg       import openapi

from firerest.settings import ADMIN_URL
from firerest.views    import IndexView, admin_redirect


schema_view = get_schema_view(
    openapi.Info(
        title='FIRELOC API',
        default_version='0.0.1',
        description="FIRELOC REST Services",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    # permission_classes=[permissions.IsAdminUser]
)

urlpatterns = [
    # Django Default backoffice
    path(f'{ADMIN_URL}/', admin_redirect, name='redirect_admin'),
    path(f'{ADMIN_URL}/admin/', admin.site.urls),
    re_path('accounts/', admin.site.urls),
    # OAUTH2 Paths
    path(f'{ADMIN_URL}/o/', include(
        'oauth2_provider.urls', namespace='oauth2_provider')),
    # Index view
    path('', IndexView.as_view(), name='index-view'),
    # Swagger View
    path('swagger/', schema_view.with_ui(
        'swagger', cache_timeout=0), name='docs-view'),
    path('redoc/', schema_view.with_ui(
        'redoc', cache_timeout=0), name='docs-view'),
    # Users management
    path('auth/', include('authapi.urls')),
    # GeoServer managemnet
    path('geosrv/', include('geosrv.urls')),
    # Contributions management
    path('volu/', include('contrib.urls')),
    # Events Management:
    path('events/', include('events.urls')),
    # Firedetect Management:
    path('floc/', include('detect.urls')),
    # GeoSpatial Reference Data management
    path('georef/', include('georef.urls')),
    # GeoSpatial Raster Datasets managment
    path('georst/', include('georst.urls')),
    # Satellite imagery related
    path('geosat/', include('geosat.urls')),
    # GeoSpatial Vector Datasets management
    path('geovec/', include('geovec.urls')),
    # GeoSpatial Data Visualization
    path('geovis/', include('geovis.urls')),
    # Meteorological Data Management
    path('meteo/',include('meteo.urls')),
    # Application logs
    path('logs/', include('logs.urls'))
]
