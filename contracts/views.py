from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from datetime import date, timedelta

from .forms import RegistrationForm, NegotiationThreadForm
from .models import Contract, Note, TrademarkRequest, LegalTask


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

    status_counts = user_contracts.values('status').annotate(count=Count('status'))
    status_data = {item['status']: item['count'] for item in status_counts}

    upcoming_milestones = user_contracts.filter(
        milestone_date__gte=date.today(),
        milestone_date__lte=date.today() + timedelta(days=30)
    ).order_by('milestone_date')

    overdue_milestones = user_contracts.filter(
        milestone_date__lt=date.today()
    ).exclude(
        status__in=[Contract.ContractStatus.RENEWAL_TERMINATION]
    ).order_by('milestone_date')

    recent_notes = Note.objects.filter(contract__in=user_contracts).order_by('-timestamp')[:5]

    context = {
        'status_data': status_data,
        'upcoming_milestones': upcoming_milestones,
        'overdue_milestones': overdue_milestones,
        'recent_notes': recent_notes,
        'total_contracts': user_contracts.count(),
    }
    return render(request, 'dashboard.html', context)


class AddNegotiationNoteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk, created_by=request.user)
        form = NegotiationThreadForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.contract = contract
            note.author = request.user
            note.save()
        return redirect('contracts:contract_detail', pk=contract.pk)


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
        return self.model.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['negotiation_form'] = NegotiationThreadForm()
        return context


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


class TrademarkRequestListView(LoginRequiredMixin, ListView):
    model = TrademarkRequest
    template_name = 'contracts/trademark_request_list.html'
    context_object_name = 'trademark_requests'

    def get_queryset(self):
        return TrademarkRequest.objects.filter(owner=self.request.user)


class LegalTaskKanbanView(LoginRequiredMixin, TemplateView):
    template_name = 'contracts/legal_task_board.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For now, showing tasks assigned to the user. This could be expanded to teams.
        tasks = LegalTask.objects.filter(assigned_to=self.request.user)

        # Prepare data in a list of tuples for easy iteration in the template
        tasks_by_status = []
        for status_key, status_display in LegalTask.TaskStatus.choices:
            tasks_in_status = tasks.filter(status=status_key)
            tasks_by_status.append((status_display, tasks_in_status))

        context['tasks_by_status'] = tasks_by_status
        return context


class LegalTaskCreateView(LoginRequiredMixin, CreateView):
    model = LegalTask
    template_name = 'contracts/legal_task_form.html'
    fields = ['title', 'task_type', 'priority', 'subject', 'is_recurring', 'assigned_to', 'due_date', 'status']
    success_url = reverse_lazy('contracts:legal_task_board')

    def form_valid(self, form):
        # If you add a 'creator' field to LegalTask, set it here:
        # form.instance.creator = self.request.user
        return super().form_valid(form)


class LegalTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = LegalTask
    template_name = 'contracts/legal_task_form.html'
    fields = ['title', 'task_type', 'priority', 'subject', 'is_recurring', 'assigned_to', 'due_date', 'status']
    success_url = reverse_lazy('contracts:legal_task_board')

    def get_queryset(self):
        # Users can only edit tasks assigned to them.
        # This could be adjusted based on team/permission rules.
        return LegalTask.objects.filter(assigned_to=self.request.user)
