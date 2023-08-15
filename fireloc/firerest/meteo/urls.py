from django.urls import path
from meteo.views.obs   import ManMeteoObservations,ManMeteoObservation
from meteo.views.src   import ManMeteoSources,ManMeteoSource
from meteo.views.st    import ManMeteoStations,ManMeteoStation
from meteo.views.var   import ManMeteoVars,ManMeteoVar
from meteo.views.forec import ManMeteoForecast,ManMeteoForec

urlpatterns = [
    # Manage Meteo Observations stuff
    path(
        'obs/', ManMeteoObservations.as_view(),
        name='manage-meteo-observations'
    ),
    path(
        'obs/<int:obsid>/', ManMeteoObservation.as_view(),
        name='manage-meteo-observation'
    ),
    # Manage Meteo Sources stuff
    path(
        'src/', ManMeteoSources.as_view(),
        name='manage-meteo-sources'
    ),
    path(
        'src/<str:slug>/', ManMeteoSource.as_view(),
        name='manage-meteo-source'
    ),
    # Manage Meteo Stations stuff
    path(
        'stations/', ManMeteoStations.as_view(),
        name='manage-meteo-stations'
    ),
    path(
        'station/<str:idapi>/', ManMeteoStation.as_view(),
        name='manage-meteo-station'
    ),
    # Manage Meteo Variables stuff
    path(
        'var/', ManMeteoVars.as_view(),
        name='manage-meteo-variables'
    ),
    path(
        'var/<str:slug>/', ManMeteoVar.as_view(),
        name='manage-meteo-variable'
    ),
    # Manage Meteo Forecast stuff
    path(
        'forecasts/', ManMeteoForecast.as_view(),
        name='manage-meteo-forecast'
    ),
    path(
        'forecast/<int:fid>/', ManMeteoForec.as_view(),
        name='manage-meteo-forec'
    )
]
