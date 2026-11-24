from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from .models import Doctor


class DoctorAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Test Admin',
            email='admin@healthcare.com',
            password='Password123'
        )
        self.doctor = Doctor.objects.create(
            name='Gregory House',
            specialization='Diagnostic Medicine',
            contact_number='+1987654321',
            email='drhouse@hospital.org',
            years_of_experience=20,
            hospital_affiliation='Princeton-Plainsboro'
        )
        self.list_create_url = reverse('doctors:doctor-list-create')
        self.client.force_authenticate(user=self.user)

    def test_create_doctor_authenticated(self):
        data = {
            'name': 'James Wilson',
            'specialization': 'Oncology',
            'contact_number': '+1987654322',
            'email': 'drwilson@hospital.org',
            'years_of_experience': 15,
            'hospital_affiliation': 'Princeton-Plainsboro'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.data['data']['name'], 'James Wilson')
        self.assertTrue(Doctor.objects.filter(email='drwilson@hospital.org').exists())

    def test_create_doctor_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'name': 'Allison Cameron',
            'specialization': 'Immunology',
            'contact_number': '+1987654323',
            'email': 'drcameron@hospital.org'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_duplicate_email(self):
        data = {
            'name': 'Duplicate Doctor',
            'specialization': 'Cardiology',
            'contact_number': '+1000000000',
            'email': 'drhouse@hospital.org'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_doctor_invalid_contact_number(self):
        data = {
            'name': 'Bad Phone Doctor',
            'specialization': 'Radiology',
            'contact_number': 'not-a-valid-phone',
            'email': 'drbad@hospital.org'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_doctor_negative_experience(self):
        data = {
            'name': 'Novice Doctor',
            'specialization': 'Pediatrics',
            'contact_number': '+1555666777',
            'email': 'drnovice@hospital.org',
            'years_of_experience': -5
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_doctors_list(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_doctor_detail(self):
        url = reverse('doctors:doctor-detail', kwargs={'pk': self.doctor.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], self.doctor.name)

    def test_update_doctor(self):
        url = reverse('doctors:doctor-detail', kwargs={'pk': self.doctor.id})
        update_data = {
            'name': 'Gregory House MD',
            'specialization': 'Diagnostics & Nephrology',
            'contact_number': '+1987654321',
            'email': 'drhouse@hospital.org',
            'years_of_experience': 21
        }
        response = self.client.put(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.name, 'Gregory House MD')
        self.assertEqual(self.doctor.years_of_experience, 21)

    def test_delete_doctor(self):
        url = reverse('doctors:doctor-detail', kwargs={'pk': self.doctor.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=self.doctor.id).exists())
