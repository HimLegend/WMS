from django.shortcuts import render
from jobcards.models import JobCard
from customers.models import Customer
from vehicles.models import Vehicle
from quotations.models import Quotation


def dashboard_view(request):
    context = {
        "customers_count": Customer.objects.count(),
        "vehicles_count": Vehicle.objects.count(),
        "jobcards_count": JobCard.objects.count(),
        "recent_jobcards": JobCard.objects.select_related('customer', 'vehicle').order_by('-created_at')[:5],
    }
    context['quotations_count'] = Quotation.objects.count()
    context['recent_quotations'] = Quotation.objects.order_by('-created_at')[:5]
    return render(request, 'core/dashboard.html', context)
