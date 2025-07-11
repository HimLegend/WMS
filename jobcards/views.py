# jobcards/views.py

from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import JobCard
from .forms import JobCardModelForm
from quotations.models import Quotation


class JobCardCreateView(CreateView):
    model = JobCard
    form_class = JobCardModelForm
    template_name = 'jobcards/create.html'
    success_url = reverse_lazy('jobcard_list')


class JobCardListView(ListView):
    model = JobCard
    template_name = 'jobcards/list.html'
    context_object_name = 'jobcards'


class JobCardDetailView(DetailView):
    model = JobCard
    template_name = 'jobcards/detail.html'
    context_object_name = 'jobcard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotation_exists'] = Quotation.objects.filter(jobcard=self.object).exists()
        return context

class JobCardUpdateView(UpdateView):
    model = JobCard
    form_class = JobCardModelForm
    template_name = 'jobcards/edit.html'
    context_object_name = 'jobcard'
    
    def get_success_url(self):
        return reverse_lazy('jobcard_detail', kwargs={'pk': self.object.pk})


class JobCardDeleteView(DeleteView):
    model = JobCard
    template_name = 'jobcards/delete_confirm.html'
    success_url = reverse_lazy('jobcard_list')
