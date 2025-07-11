# customers/views.py
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Customer
from .forms import CustomerForm

class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/create.html'
    success_url = reverse_lazy('customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/edit.html'
    success_url = reverse_lazy('customer_list')

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customers/detail.html'
    context_object_name = 'customer'

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/delete_confirm.html'
    success_url = reverse_lazy('customer_list')
