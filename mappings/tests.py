from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping


class MappingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name='Nurse Practitioner',
            email='nurse@healthcare.com',
            password='Password123'
        )
        self.patient = Patient.objects.create(
            name='Robert Chase',
            age=32,
            gender='male',
            contact_number='+1555666777',
            email='rchase@example.com',
            created_by=self.user
        )
        self.doctor = Doctor.objects.create(
            name='Lisa Cuddy',
            specialization='Endocrinology / Dean of Medicine',
            contact_number='+1555888999',
            email='drcuddy@hospital.org',
            years_of_experience=18
        )
        self.list_create_url = reverse('mappings:mapping-list-create')
        self.client.force_authenticate(user=self.user)

    def test_assign_doctor_to_patient_success(self):
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
            'notes': 'Initial consultation for thyroid review.'
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.data['data']['patient']['id'], self.patient.id)
        self.assertEqual(response.data['data']['doctor']['id'], self.doctor.id)
        self.assertTrue(
            PatientDoctorMapping.objects.filter(patient=self.patient, doctor=self.doctor).exists()
        )

    def test_assign_doctor_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_prevent_duplicate_mapping(self):
        # Create initial mapping
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)

        # Attempt to map the same doctor to the same patient again
        data = {
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success'))

    def test_retrieve_all_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_doctors_assigned_to_specific_patient(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            notes='Follow-up check'
        )
        url = reverse('mappings:mapping-detail-or-patient', kwargs={'identifier': self.patient.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.data['patient']['id'], self.patient.id)
        self.assertEqual(response.data['assigned_doctors_count'], 1)
        self.assertEqual(response.data['doctors'][0]['doctor']['id'], self.doctor.id)

    def test_get_doctors_for_nonexistent_patient(self):
        url = reverse('mappings:mapping-detail-or-patient', kwargs={'identifier': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_doctor_from_patient(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor)
        mapping_id = mapping.id
        url = reverse('mappings:mapping-detail-or-patient', kwargs={'identifier': mapping_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping_id).exists())

    def test_delete_nonexistent_mapping(self):
        url = reverse('mappings:mapping-detail-or-patient', kwargs={'identifier': 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
