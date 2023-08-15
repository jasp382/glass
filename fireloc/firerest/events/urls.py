from django.urls import path

from events.views      import ManYears, ManYear
from events.views.ev   import ManRFireEvents, ManRFireEvent, GetRFireEvents
from events.views.burn import ManBurnedAreas, ManBurnedArea
from events.views.geo  import CaopRelFireEvents, FindPlacesFreg



urlpatterns = [
    #Manage Real Fire Events
    path('real-fires/', ManRFireEvents.as_view(), name='manage-rfire-events'), 
    path('real-fire/<int:fid>/', ManRFireEvent.as_view(), name='manage-rfire-events'),
    path('rfires-uu/', GetRFireEvents.as_view(), name='list-rfire-uu'), 

    #Manage Burned Area Events 
    path('burned-areas/', ManBurnedAreas.as_view(), name='manage-burned-areas'), 
    path('burned-area/<int:fid>/', ManBurnedArea.as_view(), name='manage-burned-area'),

    #Manage Year Events
    path('years/', ManYears.as_view(), name='manage-years'), 
    path('year/<str:year>/', ManYear.as_view(), name='manage-year'),

    # Relate Fires with CAOP objects
    path(
        'firecaop/<str:caop>/', CaopRelFireEvents.as_view(),
        name="fire-events-caop"
    ),

    path(
        'fires-places/', FindPlacesFreg.as_view(),
        name='fire-find-places'
    )
]