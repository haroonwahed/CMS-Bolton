from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from datetime import date, timedelta

from .forms import RegistrationForm, NegotiationThreadForm, ChecklistItemForm
from .models import Contract, Note, TrademarkRequest, LegalTask, RiskLog, ComplianceChecklist, ChecklistItem


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
    # Contract data
    user_contracts = Contract.objects.filter(created_by=request.user)
    status_counts = {item['status']: item['count'] for item in user_contracts.values('status').annotate(count=Count('status'))}

    pipeline_stages = [
        ('DRAFT', 'Draft'),
        ('INTERNAL_REVIEW', 'Internal Review'),
        ('NEGOTIATION', 'Negotiation'),
        ('SIGNATURE', 'Signature'),
    ]
    pipeline_data = [(display, status_counts.get(key, 0)) for key, display in pipeline_stages]

    # Milestone data
    upcoming_milestones = user_contracts.filter(
        milestone_date__gte=date.today(),
        milestone_date__lte=date.today() + timedelta(days=30)
    ).order_by('milestone_date')
    overdue_milestones = user_contracts.filter(
        milestone_date__lt=date.today()
    ).exclude(
        status__in=[Contract.ContractStatus.RENEWAL_TERMINATION]
    ).order_by('milestone_date')

    # Risk data
    top_risks = RiskLog.objects.filter(risk_level='HIGH', owner=request.user).order_by('-updated_at')[:3]

    # Compliance data
    upcoming_checklists = ComplianceChecklist.objects.filter(
        due_date__gte=date.today(),
        due_date__lte=date.today() + timedelta(days=30)
    ).order_by('due_date')

    context = {
        'total_contracts': user_contracts.count(),
        'pipeline_data': pipeline_data,
        'upcoming_milestones': upcoming_milestones,
        'overdue_milestones': overdue_milestones,
        'top_risks': top_risks,
        'upcoming_checklists': upcoming_checklists,
    }
    return render(request, 'dashboard.html', context)


# --- Contract Views ---
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
    success_url = reverse_lazy('contracts:contract_list')

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


# --- Trademark Views ---
class TrademarkRequestListView(LoginRequiredMixin, ListView):
    model = TrademarkRequest
    template_name = 'contracts/trademark_request_list.html'
    context_object_name = 'trademark_requests'

    def get_queryset(self):
        return TrademarkRequest.objects.filter(owner=self.request.user)


# --- Legal Task Views ---
class LegalTaskKanbanView(LoginRequiredMixin, TemplateView):
    template_name = 'contracts/legal_task_board.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = LegalTask.objects.filter(assigned_to=self.request.user)

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


class LegalTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = LegalTask
    template_name = 'contracts/legal_task_form.html'
    fields = ['title', 'task_type', 'priority', 'subject', 'is_recurring', 'assigned_to', 'due_date', 'status']
    success_url = reverse_lazy('contracts:legal_task_board')

    def get_queryset(self):
        return LegalTask.objects.filter(assigned_to=self.request.user)


# --- Risk Log Views ---
class RiskLogListView(LoginRequiredMixin, ListView):
    model = RiskLog
    template_name = 'contracts/risk_log_list.html'
    context_object_name = 'risk_logs'

    def get_queryset(self):
        return RiskLog.objects.all()


class RiskLogCreateView(LoginRequiredMixin, CreateView):
    model = RiskLog
    template_name = 'contracts/risk_log_form.html'
    fields = ['title', 'description', 'risk_level', 'linked_contract', 'owner', 'mitigation_steps', 'mitigation_status']
    success_url = reverse_lazy('contracts:risk_log_list')


class RiskLogUpdateView(LoginRequiredMixin, UpdateView):
    model = RiskLog
    template_name = 'contracts/risk_log_form.html'
    fields = ['title', 'description', 'risk_level', 'linked_contract', 'owner', 'mitigation_steps', 'mitigation_status']
    success_url = reverse_lazy('contracts:risk_log_list')


# --- Compliance Checklist Views ---
class ComplianceChecklistListView(LoginRequiredMixin, ListView):
    model = ComplianceChecklist
    template_name = 'contracts/compliance_checklist_list.html'
    context_object_name = 'checklists'


class ComplianceChecklistDetailView(LoginRequiredMixin, DetailView):
    model = ComplianceChecklist
    template_name = 'contracts/compliance_checklist_detail.html'
    context_object_name = 'checklist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_form'] = ChecklistItemForm()
        return context


class ComplianceChecklistCreateView(LoginRequiredMixin, CreateView):
    model = ComplianceChecklist
    template_name = 'contracts/compliance_checklist_form.html'
    fields = ['name', 'regulation', 'due_date', 'attachments', 'reviewed_by', 'status']
    success_url = reverse_lazy('contracts:compliance_checklist_list')


class ComplianceChecklistUpdateView(LoginRequiredMixin, UpdateView):
    model = ComplianceChecklist
    template_name = 'contracts/compliance_checklist_form.html'
    fields = ['name', 'regulation', 'due_date', 'attachments', 'reviewed_by', 'status']
    success_url = reverse_lazy('contracts:compliance_checklist_list')


class ToggleChecklistItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(ChecklistItem, pk=pk)
        item.is_checked = not item.is_checked
        item.save()
        return redirect('contracts:compliance_checklist_detail', pk=item.checklist.pk)


class AddChecklistItemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        checklist = get_object_or_404(ComplianceChecklist, pk=pk)
        form = ChecklistItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.checklist = checklist
            item.save()
        return redirect('contracts:compliance_checklist_detail', pk=checklist.pk)
