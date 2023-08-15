from django.urls import path

from geovec.views.cats import ManVecCats, ManVecCat
from geovec.views      import ManVecDsets, ManVecDset
from geovec.views.lvl  import ManVecLevels, ManVecLevel


urlpatterns = [
    path(
        'vector-cats/', ManVecCats.as_view(),
        name='manage-vector-cats'
    ), 

    path(
        'vector-cat/<str:slug>/', ManVecCat.as_view(),
        name='manage-vector-cat'
    ), 

    path(
        'vector-datasets/', ManVecDsets.as_view(),
        name='manage-vector-datasets'
    ), 

    path(
        'vector-dataset/<str:slug>/', ManVecDset.as_view(),
        name='manage-vector-dataset'
    ),

    path(
        'vector-levels/', ManVecLevels.as_view(),
        name='manage-vector-levels'
    ), 

    path(
        'vector-level/<str:slug>/', ManVecLevel.as_view(),
        name='manage-vector-level'
    )
]