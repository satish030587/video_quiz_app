from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User

class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a superadmin user
        self.superadmin = User.objects.create_user(
            username='superadmin',
            email='superadmin@example.com',
            password='password123',
            is_superadmin=True
        )
        # Create a regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )

    def test_login(self):
        """Test user can login and get token"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_list(self):
        """Test superadmin can list users but regular users cannot"""
        url = reverse('user-list')
        
        # Unauthenticated request should be denied
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Regular user should not be able to list users
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Superadmin should be able to list users
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two users in the database