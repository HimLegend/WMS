# core/urls.py
from django.urls import path
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path('', RedirectView.as_view(url='/accounts/login/')),
    path('dashboard/', views.dashboard, name='dashboard'),
]