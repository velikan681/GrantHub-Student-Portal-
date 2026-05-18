from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Application, Category, Grant, SavedGrant


User = get_user_model()


class PortalBaseTestCase(TestCase):
    def setUp(self):
        self.category_it = Category.objects.create(name='IT')
        self.category_medicine = Category.objects.create(name='Medicine')

        self.student = User.objects.create_user(
            email='student@test.local',
            password='studentpass123',
            full_name='Student User',
            role=User.Role.STUDENT,
            university='Test University',
            faculty='Computer Science',
            course=3,
            education_level='Bachelor',
            interests='IT, startups',
        )
        self.admin = User.objects.create_user(
            email='admin@test.local',
            password='adminpass123',
            full_name='Admin User',
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.organization = User.objects.create_user(
            email='org@test.local',
            password='orgpass123',
            full_name='Organization User',
            role=User.Role.ORGANIZATION,
        )
        self.other_organization = User.objects.create_user(
            email='other-org@test.local',
            password='orgpass123',
            full_name='Other Organization',
            role=User.Role.ORGANIZATION,
        )

        self.grant = Grant.objects.create(
            title='AI Scholarship',
            description='Scholarship for IT and artificial intelligence students.',
            organization='Tech Foundation',
            country='Germany',
            category=self.category_it,
            opportunity_type=Grant.OpportunityType.SCHOLARSHIP,
            education_level='Bachelor',
            requirements='Good grades and English level B1.',
            documents='CV and motivation letter.',
            deadline=timezone.localdate() + timedelta(days=20),
            official_link='https://example.org/ai',
            created_by=self.organization,
        )
        self.medicine_grant = Grant.objects.create(
            title='Medical Exchange',
            description='Exchange program for medical students.',
            organization='Health Network',
            country='Turkey',
            category=self.category_medicine,
            opportunity_type=Grant.OpportunityType.EXCHANGE,
            education_level='Master',
            requirements='Medical background.',
            documents='CV and certificate.',
            deadline=timezone.localdate() + timedelta(days=35),
            official_link='https://example.org/medical',
            created_by=self.other_organization,
        )


class AuthenticationTests(PortalBaseTestCase):
    def test_student_can_register(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'New Student',
            'email': 'new-student@test.local',
            'university': 'New University',
            'faculty': 'Economics',
            'course': 2,
            'education_level': 'Bachelor',
            'interests': 'Economics, grants',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        })

        self.assertRedirects(response, reverse('profile'))
        user = User.objects.get(email='new-student@test.local')
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.full_name, 'New Student')

    def test_student_can_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'student@test.local',
            'password': 'studentpass123',
        })

        self.assertRedirects(response, reverse('profile'))


class GrantCatalogTests(PortalBaseTestCase):
    def test_grants_can_be_filtered_by_search_country_category_level_deadline_and_type(self):
        response = self.client.get(reverse('grants_list'), {
            'q': 'AI',
            'country': 'Germany',
            'category': str(self.category_it.id),
            'education_level': 'Bachelor',
            'deadline': (timezone.localdate() + timedelta(days=30)).isoformat(),
            'opportunity_type': Grant.OpportunityType.SCHOLARSHIP,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Scholarship')
        self.assertNotContains(response, 'Medical Exchange')

    def test_grants_api_returns_filtered_results(self):
        response = self.client.get('/grants', {'country': 'Germany'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'AI Scholarship')


class StudentActionTests(PortalBaseTestCase):
    def test_student_can_save_grant(self):
        self.client.force_login(self.student)

        response = self.client.post(reverse('save_grant', args=[self.grant.id]))

        self.assertRedirects(response, reverse('grant_detail', args=[self.grant.id]))
        self.assertTrue(SavedGrant.objects.filter(user=self.student, grant=self.grant).exists())

    def test_student_can_apply_to_grant_with_documents(self):
        self.client.force_login(self.student)
        cv_file = SimpleUploadedFile('cv.pdf', b'%PDF-1.4 test cv', content_type='application/pdf')
        motivation_file = SimpleUploadedFile('motivation.pdf', b'%PDF-1.4 test letter', content_type='application/pdf')

        response = self.client.post(
            reverse('apply_grant', args=[self.grant.id]),
            {'cv_file': cv_file, 'motivation_letter': motivation_file},
        )

        self.assertRedirects(response, reverse('my_applications'))
        application = Application.objects.get(user=self.student, grant=self.grant)
        self.assertEqual(application.status, Application.Status.REVIEW)
        self.assertTrue(application.cv_file.name.endswith('.pdf'))


class AccessControlTests(PortalBaseTestCase):
    def test_student_cannot_open_management_dashboard(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_admin_can_open_dashboard_users_and_categories(self):
        self.client.force_login(self.admin)

        for url_name in ['dashboard', 'users_list', 'manage_categories', 'manage_applications']:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, url_name)

    def test_organization_can_edit_only_own_grants(self):
        self.client.force_login(self.organization)

        own_response = self.client.get(reverse('grant_update', args=[self.grant.id]))
        other_response = self.client.get(reverse('grant_update', args=[self.medicine_grant.id]))

        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(other_response.status_code, 403)

    def test_organization_sees_only_applications_for_own_grants(self):
        Application.objects.create(user=self.student, grant=self.grant)
        other_student = User.objects.create_user(
            email='second-student@test.local',
            password='studentpass123',
            full_name='Second Student',
            role=User.Role.STUDENT,
        )
        Application.objects.create(user=other_student, grant=self.medicine_grant)
        self.client.force_login(self.organization)

        response = self.client.get(reverse('manage_applications'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Scholarship')
        self.assertNotContains(response, 'Medical Exchange')

    def test_admin_can_change_application_status(self):
        application = Application.objects.create(user=self.student, grant=self.grant)
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('update_application_status', args=[application.id]),
            {'status': Application.Status.APPROVED},
        )

        self.assertRedirects(response, reverse('manage_applications'))
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.APPROVED)

    def test_admin_can_export_excel_report(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('export_excel'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIn('granthub-admin-report.xlsx', response['Content-Disposition'])
        self.assertGreater(len(response.content), 1000)

    def test_organization_can_export_scoped_excel_report(self):
        self.client.force_login(self.organization)

        response = self.client.get(reverse('export_excel'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('granthub-organization-report.xlsx', response['Content-Disposition'])


class RecommendationTests(PortalBaseTestCase):
    def test_recommendations_match_student_profile(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse('recommendations'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Scholarship')
        self.assertNotContains(response, 'Medical Exchange')

    def test_recommendations_api_returns_matching_grants(self):
        self.client.force_login(self.student)

        response = self.client.get('/recommendations')

        self.assertEqual(response.status_code, 200)
        titles = [item['title'] for item in response.json()['results']]
        self.assertIn('AI Scholarship', titles)
        self.assertNotIn('Medical Exchange', titles)
