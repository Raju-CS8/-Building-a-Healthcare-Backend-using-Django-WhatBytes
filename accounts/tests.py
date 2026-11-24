from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.me_url = reverse('accounts:me')
        self.health_url = reverse('health-check')

        self.user_data = {
            'name': 'Dr. Alice Smith',
            'email': 'alice@healthcare.com',
            'password': 'SecurePassword123'
        }
        self.user = User.objects.create_user(
            name='Existing User',
            email='existing@healthcare.com',
            password='ExistingPassword123'
        )

    def test_health_check_endpoint(self):
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['database'], 'connected')

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('success'))
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_user_registration_duplicate_email(self):
        data = {
            'name': 'Duplicate User',
            'email': 'existing@healthcare.com',
            'password': 'Password123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success'))

    def test_user_registration_short_password(self):
        data = {
            'name': 'Short Pass',
            'email': 'short@healthcare.com',
            'password': '123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        login_data = {
            'email': 'existing@healthcare.com',
            'password': 'ExistingPassword123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'existing@healthcare.com')

    def test_user_login_invalid_password(self):
        login_data = {
            'email': 'existing@healthcare.com',
            'password': 'WrongPassword999'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_nonexistent_email(self):
        login_data = {
            'email': 'nonexistent@healthcare.com',
            'password': 'SomePassword123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_endpoint_authenticated(self):
        login_data = {
            'email': 'existing@healthcare.com',
            'password': 'ExistingPassword123'
        }
        login_resp = self.client.post(self.login_url, login_data, format='json')
        token = login_resp.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'existing@healthcare.com')

    def test_me_endpoint_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
