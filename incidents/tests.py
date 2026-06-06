from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Incident

class IncidentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_report_id_auto_generation(self):
        # Create an incident and check if a report ID is automatically generated
        incident = Incident.objects.create(
            reporter=self.user,
            title="Test Incident",
            incident_type="PHISHING",
            description="Phishing attempt detected.",
            severity="MEDIUM"
        )
        self.assertIsNotNone(incident.report_id)
        self.assertTrue(incident.report_id.startswith("REP-"))
        self.assertEqual(len(incident.report_id), 12)  # REP- + 8 characters = 12

    def test_report_id_uniqueness(self):
        # Create two incidents and check that they have distinct report IDs
        incident_1 = Incident.objects.create(
            reporter=self.user,
            title="Test 1",
            incident_type="MALWARE",
            description="Malware on server",
            severity="HIGH"
        )
        incident_2 = Incident.objects.create(
            reporter=self.user,
            title="Test 2",
            incident_type="DATA_BREACH",
            description="Database leak",
            severity="CRITICAL"
        )
        self.assertNotEqual(incident_1.report_id, incident_2.report_id)

class TrackReportViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.incident = Incident.objects.create(
            reporter=self.user,
            title="Database Breach",
            incident_type="DATA_BREACH",
            description="Database leaked online",
            severity="CRITICAL"
        )

    def test_track_page_get_empty(self):
        response = self.client.get(reverse('track_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'incidents/track_report.html')
        self.assertNotIn('incident', response.context)

    def test_track_page_get_not_found(self):
        response = self.client.get(reverse('track_report'), {'report_id': 'REP-NOTFOUND'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('error_msg', response.context)
        self.assertEqual(response.context['error_msg'], "No incident report found with ID 'REP-NOTFOUND'.")

    def test_track_page_get_success(self):
        response = self.client.get(reverse('track_report'), {'report_id': self.incident.report_id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('incident', response.context)
        self.assertEqual(response.context['incident'], self.incident)
        self.assertEqual(response.context['step'], 1)  # SUBMITTED status
        self.assertEqual(response.context['progress_pct'], 0)

class AdminPortalTest(TestCase):
    def setUp(self):
        # Create normal user
        self.user = User.objects.create_user(username='regularuser', password='password123')
        # Create staff user
        self.admin = User.objects.create_superuser(username='adminuser', password='adminpassword')
        # Create test incident
        self.incident = Incident.objects.create(
            reporter=self.user,
            title="Adware Infection",
            incident_type="MALWARE",
            description="Malicious adware detected.",
            severity="LOW",
            status="SUBMITTED"
        )

    def test_admin_login_as_regular_user(self):
        response = self.client.post(reverse('admin_login'), {
            'username': 'regularuser',
            'password': 'password123'
        })
        # Should redirect back to admin login page due to access denied logic
        self.assertRedirects(response, reverse('admin_login'))

    def test_admin_login_as_staff(self):
        response = self.client.post(reverse('admin_login'), {
            'username': 'adminuser',
            'password': 'adminpassword'
        })
        # Should redirect to the home page after admin login
        self.assertRedirects(response, reverse('home'))

    def test_admin_update_status_post(self):
        self.client.login(username='adminuser', password='adminpassword')
        
        response = self.client.post(
            reverse('admin_update_status', kwargs={'pk': self.incident.pk}),
            {'status': 'INVESTIGATING'}
        )
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, 'INVESTIGATING')
        # Should redirect back to the home page when no referring page is available
        self.assertRedirects(response, reverse('home'))


