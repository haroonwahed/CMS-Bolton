from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import date, timedelta
from .forms import RegistrationForm
from .models import Contract, Note

class SignUpView(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


@login_required
def dashboard(request):
    user_contracts = Contract.objects.filter(created_by=request.user)

    # Contract counts by status
    status_counts = user_contracts.values('status').annotate(count=Count('status'))
    status_data = {item['status']: item['count'] for item in status_counts}

    # Upcoming milestones (next 30 days)
    upcoming_milestones = user_contracts.filter(
        milestone_date__gte=date.today(),
        milestone_date__lte=date.today() + timedelta(days=30)
    ).order_by('milestone_date')

    # Overdue milestones
    overdue_milestones = user_contracts.filter(
        milestone_date__lt=date.today()
    ).exclude(
        status__in=[Contract.ContractStatus.RENEWAL_TERMINATION]
    ).order_by('milestone_date')

    # Recent notes
    recent_notes = Note.objects.filter(contract__in=user_contracts).order_by('-timestamp')[:5]

    context = {
        'status_data': status_data,
        'upcoming_milestones': upcoming_milestones,
        'overdue_milestones': overdue_milestones,
        'recent_notes': recent_notes,
        'total_contracts': user_contracts.count(),
    }
    return render(request, 'dashboard.html', context)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView


class ContractListView(LoginRequiredMixin, ListView):
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'

    def get_queryset(self):
        return Contract.objects.filter(created_by=self.request.user)


class ContractDetailView(LoginRequiredMixin, DetailView):
    model = Contract
    template_name = 'contracts/contract_detail.html'

    def get_queryset(self):
        return Contract.objects.filter(created_by=self.request.user)


class ContractCreateView(LoginRequiredMixin, CreateView):
    model = Contract
    template_name = 'contracts/contract_form.html'
    fields = ['title', 'counterparty', 'contract_type', 'jurisdiction', 'value', 'status', 'milestone_date', 'tags']
    success_url = reverse_lazy('contract_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    model = Contract
    template_name = 'contracts/contract_form.html'
    fields = ['title', 'counterparty', 'contract_type', 'jurisdiction', 'value', 'status', 'milestone_date', 'tags']
    success_url = reverse_lazy('contract_list')

    def get_queryset(self):
        return Contract.objects.filter(created_by=self.request.user)
