from django.urls import path
from .views import (
    QuotationListView,
    QuotationDetailView,
    QuotationCreateView,
    QuotationUpdateView,
    QuotationPDFView,
    SelectJobcardView,
)

urlpatterns = [
    path('select-jobcard/', SelectJobcardView.as_view(), name='select_jobcard'),
    path('', QuotationListView.as_view(), name='quotation_list'),
    path('<int:pk>/', QuotationDetailView.as_view(), name='quotation_detail'),
    path('<int:pk>/edit/', QuotationUpdateView.as_view(), name='quotation_edit'),
    path('quotations/create/<int:jobcard_pk>/', QuotationCreateView.as_view(), name='quotation_create'),
    path('<int:pk>/pdf/', QuotationPDFView.as_view(), name='quotation_pdf'),
]
