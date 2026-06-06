from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('report/', views.IncidentCreateView.as_view(), name='report_incident'),
    path('track/', views.TrackReportView.as_view(), name='track_report'),
    path('admin-portal/login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin-portal/incident/<int:pk>/update-status/', views.AdminUpdateStatusView.as_view(), name='admin_update_status'),
    path('incident/<int:pk>/', views.IncidentDetailView.as_view(), name='incident_detail'),
    path('search/', views.IncidentSearchView.as_view(), name='search'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
