# jobcards/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView
from .models import JobCard
from quotations.models import Quotation
from .forms import JobCardModelForm

class ActiveJobCardListView(ListView):
    model = JobCard
    template_name = 'jobcards/list.html'
    context_object_name = 'jobcards'
    ordering = ['-date', '-id']

    def get_queryset(self):
        return JobCard.active.all().order_by('-date', '-id')

class CompletedJobCardListView(ListView):
    model = JobCard
    template_name = 'jobcards/list.html'
    context_object_name = 'jobcards'
    ordering = ['-date', '-id']

    def get_queryset(self):
        return JobCard.completed.all().order_by('-date', '-id')

class JobCardListView(ListView):
    model = JobCard
    template_name = 'jobcards/list.html'
    context_object_name = 'jobcards'
    ordering = ['-date', '-id']

class JobCardCreateView(CreateView):
    model = JobCard
    form_class = JobCardModelForm
    template_name = 'jobcards/create.html'
    success_url = reverse_lazy('jobcard_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        
        # Save job notes (many-to-one)
        job_notes = self.request.POST.getlist('job_notes[]')
        for note in job_notes:
            note_text = note.strip()
            if note_text:
                self.object.job_notes.create(note=note_text)
                
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('jobcard_detail', kwargs={'pk': self.object.pk})

class JobCardDetailView(DetailView):
    model = JobCard
    template_name = 'jobcards/detail.html'
    context_object_name = 'jobcard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotation_exists'] = hasattr(self.object, 'quotation')
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs


class JobCardPrintView(DetailView):
    model = JobCard
    template_name = 'jobcards/print_jobcard.html'
    context_object_name = 'jobcard'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotation_exists'] = hasattr(self.object, 'quotation')
        return context


class JobCardUpdateView(UpdateView):
    model = JobCard
    form_class = JobCardModelForm
    template_name = 'jobcards/edit.html'
    context_object_name = 'jobcard'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        # Save job notes (many-to-one)
        job_notes = self.request.POST.getlist('job_notes[]')  # <- note the '[]'
        self.object.job_notes.all().delete()  # Clear existing notes

        for note in job_notes:
            note_text = note.strip()
            if note_text:
                self.object.job_notes.create(note=note_text)

        return response

    def get_success_url(self):
        return reverse_lazy('jobcard_detail', kwargs={'pk': self.object.pk})

class JobCardDeleteView(DeleteView):
    model = JobCard
    template_name = 'jobcards/delete_confirm.html'
    success_url = reverse_lazy('jobcard_list')