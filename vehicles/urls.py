from django.urls import path
from .views import (
    VehicleListView, VehicleCreateView, VehicleUpdateView,
    VehicleDetailView, VehicleDeleteView
)

urlpatterns = [
    path("", VehicleListView.as_view(), name="vehicle_list"),
    path("create/", VehicleCreateView.as_view(), name="vehicle_create"),
    path("<int:pk>/", VehicleDetailView.as_view(), name="vehicle_detail"),
    path("<int:pk>/edit/", VehicleUpdateView.as_view(), name="vehicle_edit"),
    path("<int:pk>/delete/", VehicleDeleteView.as_view(), name="vehicle_delete"),
]
