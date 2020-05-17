"""
WebGIS.Engine.API URLS
"""

from django.urls import path, include

from weapi.views import del_table, view_via_api
from weapi.views import ListDatasetsById, GetGeoServerCon, YearsView

from weapi.views.su.lstsu import StatUnitsList
from weapi.views.su.addsu import add_grpstat, add_statgeom, del_su

from weapi.views.themelyr import IndicatorsView

from weapi.views.cases.lstcase import ListCasesView, PolyLyrLst
from weapi.views.cases.lstcase import IndicatorsLyrView, PntLyrLst, IndicatorLyrByYear
from weapi.views.cases.addcase import add_case, del_case
from weapi.views.cases.addyr   import add_indicator_nomap, addpntlyr
from weapi.views.cases.addyr   import addpolylyr
from weapi.views.cases.delyr   import delpntlyr, del_indicatorlyr
from weapi.views.cases.delyr   import delpolylyr

from weapi.views.gsrv import get_wfs, get_featinfo

from weapi.views.styles import ListStyles

gsrv_patterns = [
    # WFS via Django
    path('wfs/<str:lyr>/', get_wfs, name='wfs-via-django'),
    # Get Feature Info
    path('featinfo/<str:work>/<str:lyr>/', get_featinfo, name='feature-info')
]

cases_patterns = [
    path('lstcases/', ListCasesView.as_view(), name='list-cases'),
    # Add new case
    path('addcase/', add_case, name='add-case'),
    # Delete case
    path('delcase/<str:case_id>/', del_case, name='del-case'),
    # Add Multiple Indicators Data
    path('addindsdata/', add_indicator_nomap, name='add-indicators-nomap'),
    # List Indicators Layers
    path('indicators/', IndicatorsLyrView.as_view(), name='list-indicator-layer'),
    # List Indicators Layers By Year
    path('indicatorsbyear/', IndicatorLyrByYear.as_view(), name='list_indicator-by-year'),
    # Delete Indicator Layer
    path('delindlyr/', del_indicatorlyr, name='del-indicator-layer'),
    # List Point Layers
    path('lstpntlyr/', PntLyrLst.as_view(), name='list-point-layer'),
    # Add Point Layer
    path('addpntlyr/', addpntlyr, name='add-point-layer'),
    # Delete Point Layer
    path('delpntlyr/<str:lyrid>/', delpntlyr, name='del-pnt-lyr'),
    # List Polygon Layers
    path('lstpolylyr/', PolyLyrLst.as_view(), name='lst-poly-lyr'),
    # Add categorical polygons layer
    path('addpolylyr/', addpolylyr, name='add-poly-lyr'),
    # Delete Polygon Layer
    path('delpolylyr/<str:lyrid>/', delpolylyr, name='del-poly-lyr')
]

su_patterns = [
    path('lstsu/', StatUnitsList.as_view(), name='list-su'),
    path('addsu/', add_grpstat, name='add-su-geom'),
    path('mapsucols/', add_statgeom, name='add-su-geom-cols'),
    path('delsu/<str:idgrp>/', del_su, name='delete-su-grp')
]

themelyr_pt = [
    path('lst-theme-lyr/', IndicatorsView.as_view(), name='indicators-list')
]

urlpatterns = [
    path('geoserver/', GetGeoServerCon.as_view(), name='geoserver-param'),
    # List years
    path('years/list/', YearsView.as_view(), name='list-years'),
    path('datasets/table/', ListDatasetsById.as_view(), name='list-datasets'),
    path('su/', include(su_patterns)),
    path('tlyr/', include(themelyr_pt)),
    path('cases/', include(cases_patterns)),
    # Delete data of any table
    path('deltbl/<str:table>/', del_table, name='del-table-data'),
    # SQL Views Data to Http Response
    path('dbviews/<str:view>/', view_via_api, name='view-data-http'),
    # Geoserver
    path('gsrv/', include(gsrv_patterns)),
    # Styles
    path('styles/list/', ListStyles.as_view(), name='styles-list')
]