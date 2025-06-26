from django.shortcuts import render
from jobcards.models import JobCard
# from django.contrib.auth.decorators import login_required

# @login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

def dashboard(request):
    context = {
        'jobs': JobCard.objects.all(),
        # Add other data needed for dashboard
    }
    return render(request, 'core/dashboard.html', context)