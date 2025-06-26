from django.views.generic import ListView, CreateView, UpdateView, DetailView
from .models import JobCard
from .forms import JobCardForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

class JobCardListView(ListView):
    model = JobCard
    template_name = 'jobcards/list.html'
    context_object_name = 'jobcards'
    paginate_by = 10

    def get_queryset(self):
        return JobCard.objects.select_related('vehicle', 'assigned_technician')

class JobCardCreateView(CreateView):
    model = JobCard
    form_class = JobCardForm
    template_name = 'jobcards/create.html'
    success_url = '/jobcards/'

class JobCardUpdateView(UpdateView):
    model = JobCard
    form_class = JobCardForm
    template_name = 'jobcards/update.html'
    success_url = '/jobcards/'

class JobCardDetailView(DetailView):
    model = JobCard
    template_name = 'jobcards/detail.html'

@require_http_methods(["PATCH"])
def update_jobcard_status(request, pk):
    try:
        jobcard = JobCard.objects.get(pk=pk)
        jobcard.status = request.JSON.get('status')
        jobcard.save()
        return JsonResponse({'success': True})
    except JobCard.DoesNotExist:
        return JsonResponse({'success': False}, status=404)