"""
Fire location assessment URLS
"""

from django.urls import path

from detect.views.attr  import FirelocAttrs, MFirelocAttr
from detect.views.attr  import PhotocAttrs, PhotoAttr
from detect.views.aprch import ManFlocApproachs, ManFlocApproach
from detect.views.floc  import ManFlocAssess, ManFlocResult, GetFlocAssess
from detect.views.floc  import FlocContributions, FirelocLayerData
from detect.views.photo import ManPhotoClassis, ManPhotoClass
from detect.views.sun   import ManSunData
from detect.views.geo   import FindPlacesFreg
from detect.views.near  import OldLocsNearNew



urlpatterns = [
    # Manage Fireloc Assessment stuff
    path(
        'floc-attrs/', FirelocAttrs.as_view(),
        name="manage-fireloc-attrs"
    ),
    path(
        'floc-attr/<str:slug>/', MFirelocAttr.as_view(),
        name="manage-fireloc-attr"
    ),
    path(
        'floc-approachs/', ManFlocApproachs.as_view(),
        name="manage-fireloc-approachs"
    ),
    path(
        'floc-approach/<str:slug>/', ManFlocApproach.as_view(),
        name="manage-fireloc-approach"),
    path(
        'fireloc/', ManFlocAssess.as_view(),
        name="manage-fireloc-results"
    ),
    path(
        'fireloc-i/<int:flocid>/', ManFlocResult.as_view(),
        name="manage-fireloc-result"
    ),
    path(
        'fireloc-uu/', GetFlocAssess.as_view(),
        name='list-fireloc-results-uu'
    ),

    path(
        'floc-ctbs/<int:flocid>/', FlocContributions.as_view(),
        name='relate-floc-contrib'
    ),

    path(
        'floc-raster/<str:lyr>/', FirelocLayerData.as_view(),
        name='fireloc-raster-data'
    ),

    # Manage Photo classification stuff
    path(
        'photos-class/', ManPhotoClassis.as_view(),
        name='photo-classification-results'
    ),
    path(
        'photo-class/<int:photoid>/', ManPhotoClass.as_view(),
        name='photo-classification-result'
    ),
    
    path(
        'photocls-attrs/', PhotocAttrs.as_view(),
        name='manage-photo-class-attrs'
    ),
    path(
        'photocls-attr/<str:slug>/', PhotoAttr.as_view(),
        name='manage-photo-class-attr'
    ),

    # Sun declination
    path(
        'sun-declination/', ManSunData.as_view(),
        name='manage-sun-data'
    ),

    # Places and Freguesias
    path(
        'floc-places/', FindPlacesFreg.as_view(),
        name='floc-find-places'
    ),

    # Near firelocs
    path(
        'floc-near-floc/', OldLocsNearNew.as_view(),
        name='fireloc-near-fireloc'
    )
]