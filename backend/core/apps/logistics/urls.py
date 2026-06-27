from django.urls import path

from .views import CityListCreateView, CityRetrieveUpdateDestroyView, HubListCreateView, HubRetrieveDestroyUpdate

urlpatterns = [
    path("cities/", CityListCreateView.as_view(), name="cities"),
    path("City/<int:pk>", CityRetrieveUpdateDestroyView.as_view(), name="city"),
    path("hubs/", HubListCreateView.as_view(), name="hubs"),
    path("hub/<int:pk>", HubRetrieveDestroyUpdate.as_view(), name="hub"),
]
