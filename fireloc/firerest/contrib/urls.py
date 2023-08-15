"""
Volunteers Contributions Managment - URLS Routing
"""

from django.urls import path

from contrib.views       import ManContributions, ManVContribution
from contrib.views.photo import PhotoData, DownloadPhoto
from contrib.views.az    import ManContribAzimutes, ManContribAzimute
from contrib.views.geo   import FindPlaces
from contrib.views.fxrst import FxFile, DownFxFile
from contrib.views.ctbi  import CtbIntersectCtb, CtbGroupsValidate

urlpatterns = [
    path(
        'contributions/', ManContributions.as_view(),
        name='manage-contributions'
    ),

    # Deal with single contribution
    path(
        'contribution/<int:fid>/', ManVContribution.as_view(),
        name='manage-contribution'
    ),

    # Return Photo data
    path(
        'photo/<str:picname>/', PhotoData.as_view(),
        name='get-photo-data'
    ),
    
    # Return Photo data
    path(
        'photo-download/<str:picname>/', DownloadPhoto.as_view(),
        name='download-photo'
    ),

    # Azimutes
    path(
        'ctb-azimutes/<int:ctb>/<str:geom>/',
        ManContribAzimutes.as_view(), name='manage-ctb-azimutes'
    ),

    path(
        'ctb-azimute/<int:ctb>/<str:geom>/<int:pid>/',
        ManContribAzimute.as_view(), name='manage-ctb-azimute'
    ),

    # Places
    path(
        'ctb-places/', FindPlaces.as_view(),
        name='contributions-places'
    ),

    # Contributions Raster
    path(
        'ctb-fx/<int:ctb>/', FxFile.as_view(),
        name='contribution-raster'
    ),

    # Contributions intersection
    path(
        'ctb-i-ctb/<int:step>/', CtbIntersectCtb.as_view(),
        name='contributions-intersection'
    ),

    path(
        'ctb-val/', CtbGroupsValidate.as_view(),
        name='ctb-intersection-validation'
    ),

    # Download Contribution Raster
    path(
        'fx-download/<int:ctb>/', DownFxFile.as_view(),
        name='download-ctb-raster'
    )
]