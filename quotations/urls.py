from django.urls import path
from .views import (
    QuotationListView,
    QuotationDetailView,
    QuotationCreateView,
    QuotationUpdateView,
    QuotationPDFView,
)

urlpatterns = [
    path('', QuotationListView.as_view(), name='quotation_list'),
    path('<int:pk>/', QuotationDetailView.as_view(), name='quotation_detail'),
    path('<int:pk>/edit/', QuotationUpdateView.as_view(), name='quotation_edit'),
    path('create/<int:jobcard_pk>/', QuotationCreateView.as_view(), name='quotation_create'),
    path('<int:pk>/pdf/', QuotationPDFView.as_view(), name='quotation_pdf'),
]
