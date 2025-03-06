from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from backend.models import Product, Shop, Category, ProductInfo
from rest_framework.test import APIClient

class ThrottleTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_anon_rate_throttle(self):
        url = reverse('backend:shops')
        for _ in range(10):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('detail', response.json())

    def test_user_rate_throttle(self):
        self.user = get_user_model().objects.create_user(
        email='testuser@example.com',
        password='Password123!',
        first_name='Test',
        last_name='User'
        )
        self.user.is_active = True
        self.user.save()
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        url = reverse('backend:shops')

        for _ in range(20):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('detail', response.json())

class RegisterAccountTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()

    def test_register_account_valid(self):
        url = reverse('backend:user-register')
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'password': 'Password123!',
            'company': 'Example Co',
            'position': 'Manager'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_register_account_invalid_password(self):
        url = reverse('backend:user-register') 
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'password': '123',
            'company': 'Example Co',
            'position': 'Manager'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], False)
        self.assertIn('password', response.json()['Errors'])
        
class LoginAccountTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='Password123!',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = True
        self.user.save()

    def test_login_account_valid(self):
        url = reverse('backend:user-login')
        data = {
            'email': 'testuser@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)
        self.assertTrue('Token' in response.json())

    def test_login_account_invalid(self):
        url = reverse('backend:user-login')
        data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], False)
        self.assertEqual(response.json()['Errors'], 'Не удалось авторизовать')


class AccountDetailsTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='Password123!',
            first_name='Test',
            last_name='User'
        )
        self.user.is_active = True
        self.user.save()
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)


    def test_get_account_details(self):
        url = reverse('backend:user-details')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['first_name'], 'Test')

    def test_post_account_details(self):
        url = reverse('backend:user-details')
        data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)


class ProductInfoViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.shop = Shop.objects.create(name="Test Shop", state=True)
        self.category = Category.objects.create(name="Test Category")
        
        self.product = Product.objects.create(name="Test Product", category=self.category)
        self.product_info = ProductInfo.objects.create(
            shop=self.shop,
            product=self.product,
            price=10.0,
            quantity=5,
            price_rrc=12.0,
            external_id=12345
        )

    def test_get_product_info(self):
        url = reverse('backend:products')
        response = self.client.get(url, {'shop_id': self.shop.id, 'category_id': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.json()), 0)



