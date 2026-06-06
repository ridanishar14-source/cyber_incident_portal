import secrets
import string
from django.db import models
from django.contrib.auth.models import User

class Incident(models.Model):
    INCIDENT_TYPES = [
        ('PHISHING', 'Phishing'),
        ('MALWARE', 'Malware'),
        ('DATA_BREACH', 'Data Breach'),
        ('ACCOUNT_COMPROMISE', 'Account Compromise'),
        ('OTHER', 'Other'),
    ]

    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('INVESTIGATING', 'Investigating'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='incidents', null=True, blank=True)
    report_id = models.CharField(max_length=12, unique=True, null=True, blank=True, editable=False)
    title = models.CharField(max_length=200)
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    evidence = models.FileField(upload_to='incident_evidence/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.report_id:
            while True:
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                new_id = f"REP-{code}"
                if not Incident.objects.filter(report_id=new_id).exists():
                    self.report_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.report_id or 'No ID'} - {self.title} - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']

