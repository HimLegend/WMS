from django.urls import path
from django.views.generic import RedirectView
from .views import dashboard_view, register
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('register/', register, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
