from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    path('', views.ContractListView.as_view(), name='contract_list'),
    path('trademarks/', views.TrademarkRequestListView.as_view(), name='trademark_request_list'),

    # Legal Tasks
    path('legal-tasks/', views.LegalTaskKanbanView.as_view(), name='legal_task_board'),
    path('legal-tasks/new/', views.LegalTaskCreateView.as_view(), name='legal_task_create'),
    path('legal-tasks/<int:pk>/edit/', views.LegalTaskUpdateView.as_view(), name='legal_task_update'),

    # Contracts
    path('<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('new/', views.ContractCreateView.as_view(), name='contract_create'),
    path('<int:pk>/edit/', views.ContractUpdateView.as_view(), name='contract_update'),
    path('<int:pk>/add_note/', views.AddNegotiationNoteView.as_view(), name='add_negotiation_note'),
]
