from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Main app views
    path('', views.dashboard, name='dashboard'),
    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/new/', views.contract_create, name='contract_create'),
    path('contracts/<int:pk>/', views.contract_detail, name='contract_detail'),

    # Auth
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
