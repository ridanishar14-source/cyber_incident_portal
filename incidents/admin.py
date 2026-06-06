from django.contrib import admin
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'incident_type', 'severity', 'status', 'created_at')
    list_filter = ('status', 'incident_type', 'severity')
    search_fields = ('title', 'description', 'reporter__username')
    list_editable = ('status', 'severity')
