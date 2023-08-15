from django.urls import path

from georef.views import Extent
from georef.views.refgrid import ManRefGrid
from georef.views.caop    import ManNutsII, ManNutsIII, ManConcelhos, ManBGRI
from georef.views.caop    import ManNutII, ManNutIII
from georef.views.freg    import ManFregs, ManFreg
from georef.views.places  import ManPlaces, ManPlace

urlpatterns = [
    path('map-extent/', Extent.as_view(), name='manage-map-extent'),
    path('ref-grid/', ManRefGrid.as_view(), name='manage-reference-grid'),

    path('nut-ii/', ManNutsII.as_view(), name='manage-nut-ii'),
    path('nut-ii/<str:nutid>/', ManNutII.as_view(), name='manage-one-nutii'),

    path('nut-iii/', ManNutsIII.as_view(), name='manage-nut-iii'),
    path('nut-iii/<str:nutid>/', ManNutIII.as_view(), name='manage-one-nutiii'),

    path('concelhos/', ManConcelhos.as_view(), name='manage-concelhos'),

    path('freguesias/', ManFregs.as_view(), name='manage-freguesias'),
    path('freguesia/<str:code>/', ManFreg.as_view(), name='manage-freg'),

    path('bgri/', ManBGRI.as_view(), name='manage-bgri'),

    path('places/', ManPlaces.as_view(), name='manage-places'),
    path('place/<int:fid>/', ManPlace.as_view(), name='manage-place')
]