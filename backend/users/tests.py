import json
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from main import settings
from .models import CustomUser
from .utils import validate_email, get_user
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import QueryDict
from PIL import Image
import tempfile





ruta_backend = settings.RUTA_BACKEND


class LoginTestCase(TestCase):

    def setUp(self):
        CustomUser.objects.create_user(username='UserTest123', email='testemail@gmail.com', password='UserPass123', address='TestAddress', postal_code=12345, city='Sevilla', email_verified=True)
    
    def tearDown(self):
        super().tearDown()
        
    def test_login(self):
        data = {'username': 'UserTest123', 'password': 'UserPass123'}
        response = self.client.post('/users/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
    
    def test_login_diff_password(self):
        data = {'username': 'UserTest123', 'password': 'UserPass12'}
        response = self.client.post('/users/login/', data, format='json')
        self.assertEqual(response.status_code, 400)
    
    def test_login_non_existent_user(self):
        data = {'username': 'UserTest', 'password': 'UserPass12'}
        response = self.client.post('/users/login/', data, format='json')
        self.assertEqual(response.status_code, 400)
        
class UsersTestCase(TestCase):
    
    def setUp(self):
        super().setUp()
    
    def test_register_no_password(self):
        data = {'username': 'UserTest123', 'name': 'NameTest', 'address': 'AddressTest', 'postal_code': '06228', 'city': 'Sevilla'}
        response = self.client.post('/users/api/v1/users/', data, format='json')
        self.assertEqual(response.status_code, 400)
        u = CustomUser.objects.filter(username='UserTest123').exists()
        self.assertFalse(u)

    def test_register_no_username(self):
        data = {'password': 'UserPass123', 'name': 'NameTest', 'address': 'AddressTest', 'postal_code': '06228', 'city': 'Sevilla'}
        response = self.client.post('/users/api/v1/users/', data, format='json')
        self.assertEqual(response.status_code, 400)
        u = CustomUser.objects.filter(username='UserTest123').exists()
        self.assertFalse(u)

    def test_register_no_address(self):
        data = {'username': 'UserTest123', 'password': 'UserPass123', 'name': 'NameTest', 'postal_code': '06228', 'city': 'Sevilla'}
        response = self.client.post('/users/api/v1/users/', data, format='json')
        self.assertEqual(response.status_code, 400)
        u = CustomUser.objects.filter(username='UserTest123').exists()
        self.assertFalse(u)
    
    def test_register_no_postal_code(self):
        data = {'username': 'UserTest123', 'password': 'UserPass123', 'name': 'NameTest', 'address': 'AdressTest', 'city': 'Sevilla'}
        response = self.client.post('/users/api/v1/users/', data, format='json')
        self.assertEqual(response.status_code, 400)
        u = CustomUser.objects.filter(username='UserTest123').exists()
        self.assertFalse(u)

    def test_register_no_city(self):
        data = {'username': 'UserTest123', 'password': 'UserPass123', 'name': 'NameTest', 'address': 'AdressTest'}
        response = self.client.post('/users/api/v1/users/', data, format='json')
        self.assertEqual(response.status_code, 400)
        u = CustomUser.objects.filter(username='UserTest123').exists()
        self.assertFalse(u)

    def test_validate_email(self):
        valid_emails = [
            'testemail@gmail.com',
            'user123@example.co.uk',
            'user.name@subdomain.example.com',
            'first.last@subdomain.example.com'
        ]
        for email in valid_emails:
            self.assertTrue(validate_email(email))

        invalid_emails = [
            'user@example_com',
            'user@.com',
            'user@example.',
            '@example.com'
        ]
        for email in invalid_emails:
            self.assertFalse(validate_email(email))

    def test_get_user(self):
        user = CustomUser.objects.create_user(username='TestUser', email='test@example.com', password='TestPassword', address='TestAddress', postal_code=12345, city='Sevilla')
        uidb64 = urlsafe_base64_encode(force_str(user.pk).encode())
        retrieved_user = get_user(uidb64)
        self.assertEqual(user, retrieved_user)

class RegisterWithPictureTestCase(TestCase):
    def test_register_with_picture(self):
        file_content = b'contenido'

        image= SimpleUploadedFile('dummy.jpg', file_content, content_type='image/jpeg')
        data = {'username': 'UserTest123', 'email': 'email@test.com', 'password': 'UserPass123', 'name': 'NameTest', 'address': 'AddressTest', 'postal_code': '06228', 'city': 'Sevilla','file': image}
        response = self.client.post('/users/api/v1/users/', data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(username='UserTest123').exists())
        u = CustomUser.objects.get(username='UserTest123')
        self.assertIsNotNone(u.profile_picture)

class FollowToggleTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword', address='TestAddress', postal_code=12345, city='Sevilla')
        self.client.force_authenticate(user=self.user)
        self.other_user = CustomUser.objects.create_user(username='otheruser', email='other@example.com', password='otherpassword', address='TestAddress', postal_code=12345, city='Sevilla')

    def test_follow_toggle(self):
        url = reverse('follow_toggle', kwargs={'user_id': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.user.followings.filter(id=self.other_user.id).exists())
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response.json(), {'success': 'Ahora sigues a otheruser'})

    def test_follow_toggle_unfollow(self):
        url = reverse('follow_toggle', kwargs={'user_id': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.user.followings.filter(id=self.other_user.id).exists())
        response_data = json.loads(response.content)
        self.assertEqual(response.json(), {'success': 'Ahora sigues a otheruser'})
    
        url = reverse('follow_toggle', kwargs={'user_id': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response.json(), {'success': 'Ya no sigues a otheruser'})

    def test_follow_status_follows(self):
        self.user.followings.add(self.other_user)
        url = reverse('follow_status', kwargs={'user_id': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['follows'])
        self.assertEqual(response.json(), {'follows': False})

        url = reverse('follow_toggle', kwargs={'user_id': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.user.followings.filter(id=self.other_user.id).exists())
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response.json(), {'success': 'Ahora sigues a otheruser'})

        url = reverse('follow_status', kwargs={'user_id': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['follows'])
        self.assertEqual(response.json(), {'follows': True})

    def test_follow_status_not_follows(self):
        url = reverse('follow_status', kwargs={'user_id': self.other_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['follows'])
        self.assertEqual(response.json(), {'follows': False})

    def test_get_followings(self):
        url = reverse('get_followings', kwargs={'user_id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['followings']), 0)

        # Add followings for the user
        self.user.followings.add(self.other_user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['followings']), 1)
        self.assertEqual(response_data['followings'][0]['username'], 'otheruser')

class ProfileTestCase(TestCase):
    
    def setUp(self):
        CustomUser.objects.create_user(
            id=1, username='UserTest', password='UserPass123', address='TestAddress', postal_code=12345, city='Sevilla', email_verified=True)

    def tearDown(self):
        return super().tearDown()

    def test_get_profile(self):
        response = self.client.get('/users/api/v1/users/1/')
        self.assertEqual(response.status_code, 200)
    
    def test_get_profile_fail(self):
        response = self.client.get('/users/api/v1/users/2/')
        self.assertEqual(response.status_code, 404)

class MyFollowingsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(id=1, username='UserTest',email='test@example.com', password='UserPass123', address='TestAddress', postal_code=12345, city='Sevilla', email_verified=True)
        self.client.force_authenticate(user=self.user)
        CustomUser.objects.create_user(id=2, username='UserTest2',email='test2@example.com', password='UserPass123', address='TestAddress', postal_code=12345, city='Sevilla', email_verified=True)
        url = reverse('follow_toggle', kwargs={'user_id': 2})
        self.client.get(url)

    def tearDown(self):
        return super().tearDown()

    def test_my_followings(self):
        response = self.client.get('/users/api/v1/users/1/following/')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['followings'][0]['id'], 2)
        self.assertEqual(len(response_data['followings']), 1)

        response = self.client.get('/users/api/v1/users/1/get_following_count/')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['following_count'], 1)

        url = reverse('follow_toggle', kwargs={'user_id': 2})
        self.client.get(url)

        response = self.client.get('/users/api/v1/users/1/following/')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['followings']), 0)

        response = self.client.get('/users/api/v1/users/1/get_following_count/')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['following_count'], 0)
        
        


from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

class ToggleActiveTestCase(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(username='admin', email='admin@example.com', password='admin', address='TestAddress', postal_code=12345, city='Sevilla', email_verified=True, is_staff=True, is_superuser=True)
        self.admin_token = self.get_user_token('admin', 'admin')
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword', address='TestAddress', postal_code=12345, city='Sevilla')
        self.user_token = self.get_user_token('testuser', 'testpassword')

    def get_user_token(self, username, password):
        response_login = self.client.post('/users/login/', {'username': username, 'password': password}, format='json')
        return response_login.data.get('token', '')

    def test_toggle_active_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('toggle_active', kwargs={'pk': self.user.pk})
        data = {'is_active': False}  # Change active status to False
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_toggle_active_as_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('toggle_active', kwargs={'pk': self.user.pk})
        data = {'is_active': False}  # Change active status to False
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class ProfileUpdateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', password='12345', postal_code='22222')
        self.token = Token.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user, token=self.token)

        # Crear una imagen de prueba para el perfil
        self.image = Image.new('RGB', (100, 100))
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.image.save(self.temp_file, format='JPEG')
        self.temp_file.seek(0)

    def test_update_profile(self):
        # Crear los datos de la solicitud
        data = {
            'email': 'testuser@example.com',
            'city': 'Test City',
            'postal_code': '22222',
            'address': '123 Test St',
            'profile_picture': SimpleUploadedFile(name='test_image.jpg', content=self.temp_file.read(), content_type='image/jpeg'),
            'first_name': 'Test',
            'last_name': 'User',
            'description': 'This is a test user. But a description is required',
            'is_designer': True,
            'is_printer': False,
        }

        # Enviar la solicitud PATCH
        response = self.client.patch(reverse('update_profile', kwargs={'pk': self.user.pk}), data)

        if response.status_code != 200:
            print(response.content)

        # Comprobar que la respuesta tiene un estado 200
        self.assertEqual(response.status_code, 200)

        # Comprobar que los datos del usuario se han actualizado correctamente
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.city, 'Test City')
        self.assertEqual(self.user.postal_code, 22222)
        self.assertEqual(self.user.address, '123 Test St')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.description, 'This is a test user. But a description is required')
        self.assertEqual(self.user.is_designer, True)
        self.assertEqual(self.user.is_printer, False)

    def tearDown(self):
        # Cerrar el archivo temporal
        self.temp_file.close()