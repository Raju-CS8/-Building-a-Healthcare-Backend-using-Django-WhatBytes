from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from .models import Patient


class PatientAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            name='User One',
            email='user1@healthcare.com',
            password='Password123'
        )
        self.user2 = User.objects.create_user(
            name='User Two',
            email='user2@healthcare.com',
            password='Password123'
        )

        self.patient1 = Patient.objects.create(
            name='John Doe',
            age=35,
            gender='male',
            contact_number='+1234567890',
            email='john@example.com',
            created_by=self.user1
        )
        self.patient2 = Patient.objects.create(
            name='Jane Smith',
            age=28,
            gender='female',
            contact_number='+9876543210',
            email='jane@example.com',
            created_by=self.user2
        )

        self.list_create_url = reverse('patients:patient-list-create')
        self.client.force_authenticate(user=self.user1)

    def test_create_patient_authenticated(self):
        data = {
            'name': 'Bob Brown',
            'age': 45,
            'gender': 'male',
            'contact_number': '+1122334455',
            'email': 'bob@example.com',
            'medical_history': 'Hypertension diagnosed in 2021.'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.data['data']['name'], 'Bob Brown')
        self.assertEqual(response.data['data']['created_by'], self.user1.id)

    def test_create_patient_auto_computes_age_from_dob(self):
        dob = date.today() - timedelta(days=365 * 25 + 10)  # ~25 years ago
        data = {
            'name': 'Young Adult Patient',
            'date_of_birth': dob.isoformat(),
            'gender': 'other',
            'contact_number': '+1555444333'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['age'], 25)

    def test_create_patient_rejects_future_dob(self):
        future_dob = date.today() + timedelta(days=10)
        data = {
            'name': 'Future Baby',
            'date_of_birth': future_dob.isoformat(),
            'gender': 'other',
            'contact_number': '+1555444333'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_rejects_invalid_contact_number(self):
        data = {
            'name': 'Invalid Contact',
            'contact_number': 'abc-not-a-phone'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'name': 'Unauthorized Patient',
            'contact_number': '+0000000000'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_missing_required_fields(self):
        data = {
            'age': 30
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_patients_filters_by_authenticated_user(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # user1 should only see patient1, not patient2
        patient_ids = [p['id'] for p in response.data['data']]
        self.assertIn(self.patient1.id, patient_ids)
        self.assertNotIn(self.patient2.id, patient_ids)

    def test_get_patient_detail_owner(self):
        url = reverse('patients:patient-detail', kwargs={'pk': self.patient1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], self.patient1.name)

    def test_get_patient_detail_non_owner_forbidden(self):
        # user1 tries to access patient2 (created by user2)
        url = reverse('patients:patient-detail', kwargs={'pk': self.patient2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_nonexistent_patient(self):
        url = reverse('patients:patient-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_patient_owner(self):
        url = reverse('patients:patient-detail', kwargs={'pk': self.patient1.id})
        update_data = {
            'name': 'John Doe Updated',
            'contact_number': '+1234567899',
            'age': 36,
            'gender': 'male'
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient1.refresh_from_db()
        self.assertEqual(self.patient1.name, 'John Doe Updated')
        self.assertEqual(self.patient1.age, 36)

    def test_update_patient_non_owner_forbidden(self):
        url = reverse('patients:patient-detail', kwargs={'pk': self.patient2.id})
        update_data = {
            'name': 'Hacked Jane',
            'contact_number': '+1234567899'
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_patient_owner(self):
        url = reverse('patients:patient-detail', kwargs={'pk': self.patient1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=self.patient1.id).exists())

    def test_delete_patient_non_owner_forbidden(self):
        url = reverse('patients:patient-detail', kwargs={'pk': self.patient2.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Patient.objects.filter(id=self.patient2.id).exists())
