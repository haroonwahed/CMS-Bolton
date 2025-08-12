from django.shortcuts import render
from .models import LegalRequest, Category
from django.contrib.auth.decorators import login_required
from django.db.models import Count

@login_required
def dashboard(request):
    open_requests = LegalRequest.objects.filter(status='O')
    in_progress_requests = LegalRequest.objects.filter(status='P')

    requests_by_category = Category.objects.annotate(num_requests=Count('legalrequest')).filter(num_requests__gt=0)

    context = {
        'open_requests': open_requests,
        'in_progress_requests': in_progress_requests,
        'requests_by_category': requests_by_category,
    }
    return render(request, 'core/dashboard.html', context)
