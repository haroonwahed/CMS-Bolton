from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Contract
from .forms import ContractForm
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

@login_required
def dashboard(request):
    active_contracts = Contract.objects.filter(status='AC').count()

    # Contracts expiring in the next 30 days
    expiring_soon = Contract.objects.filter(
        status='AC',
        expiration_date__isnull=False,
        expiration_date__gte=timezone.now(),
        expiration_date__lte=timezone.now() + timedelta(days=30)
    ).count()

    context = {
        'active_contracts': active_contracts,
        'expiring_soon': expiring_soon,
        'app_name': 'Bolton CLM'
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def contract_list(request):
    contracts = Contract.objects.all().order_by('-created_at')
    return render(request, 'core/contract_list.html', {'contracts': contracts})


@login_required
def contract_create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user
            contract.save()
            return redirect('contract_list')
    else:
        form = ContractForm()
    return render(request, 'core/contract_form.html', {'form': form})


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


@login_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, 'core/contract_detail.html', {'contract': contract})
