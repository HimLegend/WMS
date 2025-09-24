from django.shortcuts import render
from jobcards.models import JobCard
from customers.models import Customer
from vehicles.models import Vehicle
from quotations.models import Quotation


from .forms import StyledUserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect

def dashboard_view(request):
    context = {
        "customers_count": Customer.objects.count(),
        "vehicles_count": Vehicle.objects.count(),
        "jobcards_count": JobCard.objects.count(),
        "active_jobcards_count": JobCard.active.count(),
        "completed_jobcards_count": JobCard.completed.count(),
        "recent_jobcards": JobCard.objects.select_related('customer', 'vehicle').order_by('-created_at')[:5],
    }
    context['quotations_count'] = Quotation.objects.count()
    context['recent_quotations'] = Quotation.objects.order_by('-created_at')[:5]
    return render(request, 'core/dashboard.html', context)



def register(request):
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = StyledUserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})
