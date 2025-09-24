# jobcards/urls.py
from django.urls import path
from .views import (
    JobCardCreateView, JobCardListView, JobCardDetailView, 
    JobCardUpdateView, JobCardDeleteView, ActiveJobCardListView, 
    CompletedJobCardListView, JobCardPrintView
)

urlpatterns = [
    path('active/', ActiveJobCardListView.as_view(), name='active_jobcards'),
    path('completed/', CompletedJobCardListView.as_view(), name='completed_jobcards'),
    path('', JobCardListView.as_view(), name='jobcard_list'),
    path('create/', JobCardCreateView.as_view(), name='jobcard_create'),
    path('<int:pk>/', JobCardDetailView.as_view(), name='jobcard_detail'),
    path('<int:pk>/print/', JobCardPrintView.as_view(), name='jobcard_print'),
    path('<int:pk>/edit/', JobCardUpdateView.as_view(), name='jobcard_edit'),
    path('<int:pk>/delete/', JobCardDeleteView.as_view(), name='jobcard_delete'),
]
