from django.urls import path
from . import views

app_name = 'inspections'

urlpatterns = [
    path('', views.inspection_list, name='inspection_list'),

    # Create report for a specific job card
    path('create/<int:jobcard_id>/', views.create_inspection_report, name='create_inspection_report'),

    # Edit, detail, and PDF export for inspection reports
    path('<int:pk>/edit/', views.edit_inspection_report, name='edit_inspection_report'),
    path('<int:pk>/', views.inspection_detail, name='inspection_detail'),
    path('<int:pk>/pdf/', views.inspection_pdf, name='inspection_pdf'),

    # Manage parts and consumables linked to a finding
    # path('finding/<int:finding_pk>/parts/', views.manage_parts, name='manage_parts'),
    # path('finding/<int:finding_pk>/consumables/', views.manage_consumables, name='manage_consumables'),
]
