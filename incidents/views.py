from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib import messages
from .models import Incident
import json

class HomeView(TemplateView):
    template_name = 'incidents/home.html'

class AboutView(TemplateView):
    template_name = 'incidents/about.html'

class DashboardView(LoginRequiredMixin, ListView):
    model = Incident
    template_name = 'incidents/dashboard.html'
    context_object_name = 'incidents'

    def get_queryset(self):
        return Incident.objects.filter(reporter=self.request.user)

class IncidentDetailView(LoginRequiredMixin, DetailView):
    model = Incident
    template_name = 'incidents/incident_detail.html'

    def get_queryset(self):
        return Incident.objects.filter(reporter=self.request.user)

class IncidentCreateView(CreateView):
    model = Incident
    template_name = 'incidents/incident_form.html'
    fields = ['title', 'incident_type', 'description', 'severity', 'evidence']
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.reporter = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Incident report successfully submitted! Your unique Report ID is: {self.object.report_id}"
        )
        return response

class TrackReportView(TemplateView):
    template_name = 'incidents/track_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report_id = self.request.GET.get('report_id', '').strip()
        context['report_id'] = report_id
        
        if report_id:
            try:
                incident = Incident.objects.get(report_id__iexact=report_id)
                context['incident'] = incident
                
                # Determine tracking progress bar step and percentage
                status_steps = {
                    'SUBMITTED': (1, 0),
                    'UNDER_REVIEW': (2, 25),
                    'INVESTIGATING': (3, 50),
                    'RESOLVED': (4, 75),
                    'CLOSED': (5, 100),
                }
                
                step, progress_pct = status_steps.get(incident.status, (1, 0))
                context['step'] = step
                context['progress_pct'] = progress_pct
            except Incident.DoesNotExist:
                context['error_msg'] = f"No incident report found with ID '{report_id}'."
        return context


class IncidentSearchView(LoginRequiredMixin, ListView):
    model = Incident
    template_name = 'incidents/dashboard.html'
    context_object_name = 'incidents'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Incident.objects.filter(
                Q(reporter=self.request.user) &
                (Q(title__icontains=query) | Q(description__icontains=query) | Q(incident_type__icontains=query))
            )
        return Incident.objects.filter(reporter=self.request.user)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


class AdminLoginView(LoginView):
    template_name = 'registration/admin_login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if user.is_staff or user.is_superuser:
            return super().form_valid(form)
        else:
            messages.error(self.request, "Access Denied: You do not have administrator privileges.")
            return redirect('admin_login')
            
    def get_success_url(self):
        return reverse_lazy('home')


class AdminUpdateStatusView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)
        
    def handle_no_permission(self):
        messages.error(self.request, "Access denied.")
        return redirect('home')
        
    def post(self, request, pk, *args, **kwargs):
        incident = get_object_or_404(Incident, pk=pk)
        new_status = request.POST.get('status')
        
        valid_statuses = [choice[0] for choice in Incident.STATUS_CHOICES]
        if new_status in valid_statuses:
            incident.status = new_status
            incident.save()
            messages.success(request, f"Status for incident {incident.report_id} updated to {incident.get_status_display()}.")
        else:
            messages.error(request, "Invalid status choice.")
            
        next_url = request.META.get('HTTP_REFERER', reverse_lazy('home'))
        return redirect(next_url)
