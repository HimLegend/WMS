from django.urls import path
from .views import JobCardListView, JobCardCreateView, JobCardUpdateView, JobCardDetailView

urlpatterns = [
    path('', JobCardListView.as_view(), name='jobcard-list'),
    path('create/', JobCardCreateView.as_view(), name='jobcard-create'),
    path('<int:pk>/', JobCardDetailView.as_view(), name='jobcard-detail'),
    path('<int:pk>/update/', JobCardUpdateView.as_view(), name='jobcard-update'),
]