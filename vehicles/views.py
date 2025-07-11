from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from .models import Vehicle
from .forms import VehicleForm

class VehicleListView(ListView):
    model = Vehicle
    template_name = "vehicles/list.html"
    context_object_name = "vehicles"

class VehicleCreateView(CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/create.html"
    success_url = reverse_lazy("vehicle_list")

class VehicleUpdateView(UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "vehicles/edit.html"
    success_url = reverse_lazy("vehicle_list")

class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = "vehicles/detail.html"
    context_object_name = "vehicle"

class VehicleDeleteView(DeleteView):
    model = Vehicle
    template_name = "vehicles/delete_confirm.html"
    success_url = reverse_lazy("vehicle_list")
