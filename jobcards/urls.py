# jobcards/urls.py
from django.urls import path
from .views import JobCardCreateView, JobCardListView, JobCardDetailView, JobCardUpdateView, JobCardDeleteView

urlpatterns = [
    path('', JobCardListView.as_view(), name='jobcard_list'),
    path('create/', JobCardCreateView.as_view(), name='jobcard_create'),
    path('<int:pk>/', JobCardDetailView.as_view(), name='jobcard_detail'),
    path('<int:pk>/edit/', JobCardUpdateView.as_view(), name='jobcard_edit'),
    path('<int:pk>/delete/', JobCardDeleteView.as_view(), name='jobcard_delete'),
]
