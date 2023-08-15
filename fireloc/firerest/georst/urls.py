from django.urls import path
from georst.views import ManRstTypes, ManRstDatasets,ManRstDataset
from georst.views.lyr import RstLayers
from georst.views.rfiles import RstLayerFile

urlpatterns = [
    path('raster-types/', ManRstTypes.as_view(), name='manage-raster-types'),
    path(
        'raster-datasets/', ManRstDatasets.as_view(),
        name='manage-raster-datasets'
    ),
    path(
        'raster-dataset/<str:slugid>/', ManRstDataset.as_view(),
        name='manage-raster-dataset'
    ),
    path(
        'raster-layers/', RstLayers.as_view(),
        name='manage-raster-layer'
    ),
    path(
        'raster-file/<str:rdset>/<str:layer>/', RstLayerFile.as_view(),
        name="add-raster-file"
    )
]
