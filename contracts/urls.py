from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.ContractListView.as_view(), name='contract_list'),
    path('<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('new/', views.ContractCreateView.as_view(), name='contract_create'),
    path('<int:pk>/edit/', views.ContractUpdateView.as_view(), name='contract_update'),
]
