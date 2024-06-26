import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.authtoken.admin import User
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from order.models import Order, OrderProduct
from users.models import CustomUser
from .models import Product
from .views import ProductsView


# Create your tests here.
class ProductsViewTestClase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user1 = CustomUser.objects.create(
            username='user1',
            password='test',
            address='test',
            postal_code=1234,
            city='test',
            email='test1@example.com',
            email_verified=True
        )
        self.user2 = CustomUser.objects.create(
            username='user2',
            password='test',
            address='test',
            postal_code=1234,
            city='test',
            email='test2@example.com',
            email_verified=True
        )

        # Creamos algunos productos
        self.product1 = Product.objects.create(
            product_type='I',
            price=100,
            name='Producto 1',
            description='Descripción del producto 1',
            stock_quantity=10,
            seller=self.user1,
        )
        self.product2 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 2',
            description='Descripción del producto 2',
            stock_quantity=5,
            seller=self.user2,
        )
        design3 = SimpleUploadedFile('test3.pdf', b'design_content', content_type='application/pdf')
        self.product3 = Product.objects.create(
            product_type='D',
            price=300,
            name='Producto 3',
            description='Descripción del producto 3',
            stock_quantity=1,
            seller=self.user1,
            design=design3,
        )

    def test_get_product_data(self):
        customUser = CustomUser.objects.create(
            username='test',
            password='test',
            address='test',
            postal_code=1234,
            city='test'
        )

        product = Product.objects.create(
            product_type='I',
            price=100,
            name='Producto 1',
            description='Descripción del producto 1',
            stock_quantity=10,
            seller=customUser,
        )

        response = self.client.get('/products/api/v1/products/' + str(product.id) + '/get_product_data/')
        self.assertEqual(response.status_code, 200)

    def test_get_products(self):
        response = self.client.get('/products/api/v1/products/')
        self.assertEqual(response.status_code, 200)

    def test_get_products_filtered(self):
        response = self.client.get('/products/api/v1/products/?product_type=I')
        self.assertEqual(response.status_code, 200)

    def test_get_all_products(self):
        client = APIClient()
        response = client.get(reverse('products-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_by_product_type(self):
        client = APIClient()
        response = client.get(reverse('products-list') + '?product_type=I')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.product1.id)

    def test_filter_by_seller(self):
        client = APIClient()
        response = client.get(reverse('products-list') + f'?seller={self.user2.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.product2.id)

    def test_search_by_name_or_description(self):
        client = APIClient()
        response = client.get(reverse('products-list') + '?search=Producto 1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.product1.id)

    def test_combined_filters(self):
        # Probamos combinar múltiples filtros
        client = APIClient()
        response = client.get(reverse('products-list') + '?product_type=P&search=Producto 2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.product2.id)

    def test_edit_product_success(self):
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        request = self.factory.put(url, {'price': 200, 'name': 'Updated Product', 'description': 'Updated Description',
                                         'show': 'false', 'stock_quantity': 5}, format='json')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product1.pk)
        self.assertEqual(response.status_code, 200)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.price, 200)
        self.assertEqual(self.product1.name, 'Updated Product')
        self.assertEqual(self.product1.stock_quantity, 5)

    def test_edit_product_fail_permission(self):
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        request = self.factory.put(url, {'price': 200, 'name': 'Updated Product', 'stock_quantity': 20}, format='json')
        other_user = CustomUser.objects.create(username='otheruser', password='otherpass', address='test',
                                               postal_code=1234, city='test')
        force_authenticate(request, user=other_user)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product1.pk)
        self.assertEqual(response.status_code, 403)

    def test_edit_product_not_all_validation(self):
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        request = self.factory.put(url, {'price': 2000000, 'name': 'Updated Product', 'stock_quantity': 200},
                                   format='json')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product1.pk)
        self.assertEqual(response.status_code, 400)

    def test_edit_product_negative_price_validation(self):
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        request = self.factory.put(url, {'price': -1, 'name': 'Updated Product', 'description': 'Updated Description',
                                         'show': 'true', 'stock_quantity': 20}, format='json')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product1.pk)
        self.assertEqual(response.status_code, 400)

    def test_edit_product_high_price_validation(self):
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        request = self.factory.put(url, {'price': 9999999999999, 'name': 'Updated Product',
                                         'description': 'Updated Description', 'show': 'true', 'stock_quantity': 20},
                                   format='json')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product1.pk)
        self.assertEqual(response.status_code, 400)

    def test_edit_product_stock_quantity_design_validation(self):
        url = reverse('products-detail', kwargs={'pk': self.product3.pk})
        request = self.factory.put(url, {'price': 200, 'name': 'Updated Product', 'description': 'Updated Description',
                                         'show': 'true', 'stock_quantity': 20}, format='json')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product3.pk)
        self.assertEqual(response.status_code, 200)
        self.product3.refresh_from_db()
        self.assertEqual(self.product3.product_type, 'D')
        self.assertEqual(self.product3.stock_quantity, 1)

    def test_edit_product_negative_stock_quantity_validation(self):
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        request = self.factory.put(url, {'price': 200, 'name': 'Updated Product', 'description': 'Updated Description',
                                         'show': 'true', 'stock_quantity': -1}, format='json')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product1.pk)
        self.assertEqual(response.status_code, 400)

    def test_edit_product_high_stock_quantity_validation(self):
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        request = self.factory.put(url, {'price': 200, 'name': 'Updated Product', 'description': 'Updated Description',
                                         'show': 'true', 'stock_quantity': 1000000}, format='json')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product1.pk)
        self.assertEqual(response.status_code, 400)

    def test_edit_product_image(self):
        url = reverse('products-detail', kwargs={'pk': self.product1.pk})
        image = SimpleUploadedFile('test.jpg', b'content', content_type='image/jpeg')
        request = self.factory.put(url, {'price': 200, 'name': 'Updated Product', 'description': 'Updated Description',
                                         'show': 'true', 'stock_quantity': 20, 'image': image}, format='multipart')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product1.pk)
        self.assertEqual(response.status_code, 200)
        self.product1.refresh_from_db()
        self.assertIsNotNone(self.product1.image)

    def test_edit_product_design(self):
        url = reverse('products-detail', kwargs={'pk': self.product3.pk})
        design = SimpleUploadedFile('test.pdf', b'design_content', content_type='application/pdf')
        request = self.factory.put(url, {'price': 200, 'name': 'Updated Product', 'description': 'Updated Description',
                                         'show': 'true', 'stock_quantity': 20, 'design': design}, format='multipart')
        force_authenticate(request, user=self.user1)
        response = ProductsView.as_view({'put': 'edit_product'})(request, pk=self.product3.pk)
        self.assertEqual(response.status_code, 200)
        self.product3.refresh_from_db()
        self.assertIsNotNone(self.product3.design)


class SellerPlanTestClase(TestCase):
    def setUp(self):
        # Creamos algunos usuarios y productos para usar en los tests
        self.user1 = User.objects.create_user(username='testuser1', email='test3@example.com', password='test',
                                              is_staff=True, postal_code='12345', email_verified=True, seller_plan=True)
        response = self.client.post(reverse('login'), {'username': 'testuser1', 'password': 'test'})
        self.token = response.json()["token"]

        self.user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='test',
                                              is_staff=True, postal_code='12345', email_verified=True,
                                              seller_plan=False)
        response = self.client.post(reverse('login'), {'username': 'testuser2', 'password': 'test'})
        self.token2 = response.json()["token"]

        self.product0 = Product.objects.create(
            product_type='P',
            price=100,
            name='Producto 0',
            description='Descripción del producto 0',
            stock_quantity=10,
            show=False,
            seller=self.user2,
        )

        # Creamos algunos productos
        self.product1 = Product.objects.create(
            product_type='P',
            price=100,
            name='Producto 1',
            description='Descripción del producto 1',
            stock_quantity=10,
            show=True,
            seller=self.user1,
        )
        self.product2 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 2',
            description='Descripción del producto 2',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )
        self.product3 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 3',
            description='Descripción del producto 3',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )
        self.product4 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 4',
            description='Descripción del producto 4',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

        self.product5 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 5',
            description='Descripción del producto 5',
            show=False,
            stock_quantity=5,
            seller=self.user1,
        )

    def test_ok_add_product(self):
        image_content = b'contenido_de_imagen'
        image = SimpleUploadedFile("image.jpg", image_content, content_type="image/jpeg")
        data = {
            'product_type': 'P',
            'price': 200,
            'name': 'Producto 6',
            'description': 'Descripción del producto 6',
            'show': 'true',
            'stock_quantity': 5,
            'seller': self.user1,
            'file': image}
        response = self.client.post(reverse('add_product'), data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 201)
        response = self.client.get(reverse('products-list') + '?product_type=P')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)

    def test_wrong_add_product(self):
        self.product7 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 7',
            description='Descripción del producto 7',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

        image_content = b'contenido_de_imagen'
        image = SimpleUploadedFile("image.jpg", image_content, content_type="image/jpeg")
        data = {
            'product_type': 'P',
            'price': 200,
            'name': 'Producto 6',
            'description': 'Descripción del producto 6',
            'show': 'true',
            'stock_quantity': 5,
            'seller': self.user1,
            'file': image}
        response = self.client.post(reverse('add_product'), data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 400)

    def test_non_seller_add_product(self):
        self.product8 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 8',
            description='Descripción del producto 8',
            show=True,
            stock_quantity=5,
            seller=self.user2,
        )

        image_content = b'contenido_de_imagen'
        image = SimpleUploadedFile("image.jpg", image_content, content_type="image/jpeg")
        data = {
            'product_type': 'P',
            'price': 200,
            'name': 'Producto 6',
            'description': 'Descripción del producto 6',
            'show': 'true',
            'stock_quantity': 5,
            'seller': self.user1,
            'file': image}
        response = self.client.post(reverse('add_product'), data, HTTP_AUTHORIZATION='Bearer ' + self.token2)
        self.assertEqual(response.status_code, 400)


from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class AddProductTest(APITestCase):

    def setUp(self):
        # Configuración inicial para cada prueba
        # Crear usuarios de prueba
        self.normal_user = self.create_user('normal_user', email='test11@example.com', email_verified=True)
        self.normal_token = self.get_token('normal_user', 'normal_user')

        self.designer_user = self.create_user('designer_user', email='test12@example.com', email_verified=True, designer_plan=True)
        self.designer_token = self.get_token('designer_user', 'designer_user')

        self.seller_user = self.create_user('seller_user', email= 'test13@example.com',email_verified=True, seller_plan=True)
        self.seller_token = self.get_token('seller_user', 'seller_user')

        self.seller_and_designer_user = self.create_user('seller_and_designer_user', email='test14@example.com', email_verified=True,
                                                         seller_plan=True, designer_plan=True)
        self.seller_and_designer_token = self.get_token('seller_and_designer_user', 'seller_and_designer_user')

    def create_user(self, username, email, email_verified=False, designer_plan=False, seller_plan=False):
        # Crear un usuario con parámetros opcionales
        return User.objects.create_user(
            username=username,
            password=username,
            address='test',
            postal_code=1234,
            city='test',
            email=email,
            email_verified=email_verified,
            designer_plan=designer_plan,
            seller_plan=seller_plan
        )

    def get_token(self, username, password):
        # Obtener token de autenticación para un usuario
        response = self.client.post(reverse('login'), {'username': username, 'password': password})
        return response.json()["token"]

    def create_dummy_image(self):
        # Crear una imagen dummy para usar en las pruebas
        file_content = b'dummy content'
        return SimpleUploadedFile('dummy.jpg', file_content, content_type='image/jpeg')

    def add_product_with_token(self, token):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo proyecto',
            'show': 'true',
            'price': 200,
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        return self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + token)

    def test_add_product(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo producto',
            'show': 'false',
            'price': 200,
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Name
    def test_no_name(self):
        url = reverse('add_product')
        data = {
            'description': 'Descripción del nuevo producto',
            'show': 'false',
            'price': 200,
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Todos los campos son obligatorios'})

    # Description
    def test_no_description(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'show': 'false',
            'price': 200,
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Todos los campos son obligatorios'})

    # Show
    def test_no_show(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo producto',
            'price': 200,
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Todos los campos son obligatorios'})

    def test_stand_out_as_normal_user(self):
        response = self.add_product_with_token(self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'No puedes destacar productos sin contratar un plan'})

    def test_stand_out_as_designer(self):
        for _ in range(3):
            response = self.add_product_with_token(self.designer_token)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.add_product_with_token(self.designer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Ya hay 3 productos destacados'})

    def test_stand_out_as_seller(self):
        for _ in range(5):
            response = self.add_product_with_token(self.seller_token)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.add_product_with_token(self.seller_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Ya hay 5 productos destacados'})

    def test_stand_out_as_seller_and_designer(self):
        for _ in range(8):
            response = self.add_product_with_token(self.seller_and_designer_token)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.add_product_with_token(self.seller_and_designer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Ya hay 8 productos destacados'})

    # Price
    def test_no_price(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo producto',
            'show': 'false',
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Todos los campos son obligatorios'})

    def test_invalid_price(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo proyecto',
            'show': 'true',
            'price': 'a',
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'El precio debe ser un número válido'})

    def test_negative_price(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo proyecto',
            'show': 'true',
            'price': -200,
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'El precio debe estar entre 0 y 1,000,000'})

    def test_high_price(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo proyecto',
            'show': 'true',
            'price': 2000001,
            'product_type': 'P',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'El precio debe estar entre 0 y 1,000,000'})

    # Product Type
    def test_no_product_type(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo producto',
            'show': 'false',  # Suponiendo que 'show' se espera como una cadena ('true' o 'false')
            'price': 200,
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Todos los campos son obligatorios'})

    def test_invalid_product_type(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo proyecto',
            'show': 'true',
            'price': 200,
            'product_type': 'X',
            'stock_quantity': 10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Tipo de producto no válido'})

    # Stock Quantity
    def test_no_stock_quantity(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo producto',
            'show': 'false',
            'price': 200,
            'product_type': 'P',
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Todos los campos son obligatorios'})

    def test_invalid_stock_quantity(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo proyecto',
            'show': 'true',
            'price': 200,
            'product_type': 'P',
            'stock_quantity': 'x',
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'La cantidad de stock debe ser un número entero válido'})

    def test_negative_stock_quantity(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo proyecto',
            'show': 'true',
            'price': 200,
            'product_type': 'P',
            'stock_quantity': -10,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'La cantidad debe estar entre 1 y 100'})

    def test_high_stock_quantity(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo proyecto',
            'show': 'true',
            'price': 200,
            'product_type': 'P',
            'stock_quantity': 1000001,
            'file': self.create_dummy_image()
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'La cantidad debe estar entre 1 y 100'})

    # File
    def test_no_file(self):
        url = reverse('add_product')
        data = {
            'name': 'Nuevo Producto',
            'description': 'Descripción del nuevo producto',
            'show': 'false',  # Suponiendo que 'show' se espera como una cadena ('true' o 'false')
            'price': 200,
            'product_type': 'P',
            'stock_quantity': 10
        }
        response = self.client.post(url, data, HTTP_AUTHORIZATION='Bearer ' + self.normal_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Todos los campos son obligatorios'})


class BuyerPlanTestClase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', email='test4@example.com', password='test',
                                              is_staff=True, postal_code='12345', email_verified=True, buyer_plan=True)
        response = self.client.post(reverse('login'), {'username': 'testuser1', 'password': 'test'})
        self.token = response.json()["token"]

        self.user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='test',
                                              is_staff=True, postal_code='12345', email_verified=True, buyer_plan=False)
        response2 = self.client.post(reverse('login'), {'username': 'testuser2', 'password': 'test'})
        self.token2 = response2.json()["token"]

        self.product = Product.objects.create(
            product_type='I',
            price=100,
            name='Producto 1',
            description='Descripción del producto 1',
            stock_quantity=10,
            seller=self.user2,
        )

        self.order_data = {
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'buyer_mail': 'test5@example.com',
            'cart': json.dumps([{'id': self.product.id, 'quantity': 1}]),
        }

        self.product2 = Product.objects.create(
            product_type='I',
            price=100,
            name='Producto 1',
            description='Descripción del producto 1',
            stock_quantity=10,
            seller=self.user1,
        )

        self.order_data2 = {
            'address': '123 Test Street',
            'city': 'Test City',
            'postal_code': '12345',
            'buyer_mail': 'test2@example.com',
            'cart': json.dumps([{'id': self.product2.id, 'quantity': 1}]),
        }

    def test_buy_no_send_spends(self):
        response = self.client.post(reverse('create_order'), self.order_data, format='json',
                                    HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 1)
        new_order = Order.objects.filter(buyer=self.user1).last()
        self.assertEqual(new_order.buyer, self.user1)
        self.assertEqual(OrderProduct.objects.count(), 1)
        self.assertEqual(new_order.price, 100)
        new_order_product = OrderProduct.objects.filter(order=new_order).last()
        self.assertEqual(new_order_product.order, new_order)
        self.assertEqual(new_order_product.product, self.product)
        self.assertEqual(new_order_product.quantity, 1)

    def test_buy_with_send_spends(self):
        response = self.client.post(reverse('create_order'), self.order_data2, format='json',
                                    HTTP_AUTHORIZATION='Bearer ' + self.token2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 1)
        new_order = Order.objects.filter(buyer=self.user2).last()
        self.assertEqual(new_order.buyer, self.user2)
        self.assertEqual(OrderProduct.objects.count(), 1)
        self.assertEqual(new_order.price, 105)
        new_order_product = OrderProduct.objects.filter(order=new_order).last()
        self.assertEqual(new_order_product.order, new_order)
        self.assertEqual(new_order_product.product, self.product2)
        self.assertEqual(new_order_product.quantity, 1)


class DesignerPlanTestClase(TestCase):
    def setUp(self):
        # Creamos algunos usuarios y productos para usar en los tests
        self.user1 = User.objects.create_user(username='testuser1', email='test6@example.com', password='test',
                                              is_staff=True, postal_code='12345', email_verified=True,
                                              designer_plan=True)
        response = self.client.post(reverse('login'), {'username': 'testuser1', 'password': 'test'})
        self.token = response.json()["token"]

        self.user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='test',
                                              is_staff=True, postal_code='12345', email_verified=True,
                                              designer_plan=False)
        response = self.client.post(reverse('login'), {'username': 'testuser2', 'password': 'test'})
        self.token2 = response.json()["token"]

        self.product0 = Product.objects.create(
            product_type='P',
            price=100,
            name='Producto 0',
            description='Descripción del producto 0',
            stock_quantity=10,
            show=False,
            seller=self.user2,
        )

        # Creamos algunos productos
        self.product1 = Product.objects.create(
            product_type='P',
            price=100,
            name='Producto 1',
            description='Descripción del producto 1',
            stock_quantity=10,
            show=True,
            seller=self.user1,
        )
        self.product2 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 2',
            description='Descripción del producto 2',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

        self.product3 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 5',
            description='Descripción del producto 5',
            show=False,
            stock_quantity=5,
            seller=self.user1,
        )

    def test_ok_add_product(self):
        image_content = b'contenido_de_imagen'
        image = SimpleUploadedFile("image.jpg", image_content, content_type="image/jpeg")
        data = {
            'product_type': 'P',
            'price': 200,
            'name': 'Producto 6',
            'description': 'Descripción del producto 6',
            'show': 'true',
            'stock_quantity': 5,
            'seller': self.user1,
            'file': image}
        response = self.client.post(reverse('add_product'), data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 201)
        response = self.client.get(reverse('products-list') + '?product_type=P')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_wrong_add_product(self):
        self.product7 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 7',
            description='Descripción del producto 7',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

        image_content = b'contenido_de_imagen'
        image = SimpleUploadedFile("image.jpg", image_content, content_type="image/jpeg")
        data = {
            'product_type': 'P',
            'price': 200,
            'name': 'Producto 6',
            'description': 'Descripción del producto 6',
            'show': 'true',
            'stock_quantity': 5,
            'seller': self.user1,
            'file': image}
        response = self.client.post(reverse('add_product'), data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 400)

    def test_non_seller_add_product(self):
        self.product8 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 8',
            description='Descripción del producto 8',
            show=True,
            stock_quantity=5,
            seller=self.user2,
        )

        image_content = b'contenido_de_imagen'
        image = SimpleUploadedFile("image.jpg", image_content, content_type="image/jpeg")
        data = {
            'product_type': 'P',
            'price': 200,
            'name': 'Producto 6',
            'description': 'Descripción del producto 6',
            'show': 'true',
            'stock_quantity': 5,
            'seller': self.user1,
            'file': image}
        response = self.client.post(reverse('add_product'), data, HTTP_AUTHORIZATION='Bearer ' + self.token2)
        self.assertEqual(response.status_code, 400)


class BothSellerAndDesignerPlanTestClase(TestCase):
    def setUp(self):
        # Creamos algunos usuarios y productos para usar en los tests
        self.user1 = User.objects.create_user(username='testuser1', email='test7@example.com', password='test',
                                              is_staff=True, postal_code='12345', email_verified=True, seller_plan=True,
                                              designer_plan=True)
        response = self.client.post(reverse('login'), {'username': 'testuser1', 'password': 'test'})
        self.token = response.json()["token"]

        # Creamos algunos productos
        self.product1 = Product.objects.create(
            product_type='P',
            price=100,
            name='Producto 1',
            description='Descripción del producto 1',
            stock_quantity=10,
            show=True,
            seller=self.user1,
        )
        self.product2 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 2',
            description='Descripción del producto 2',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )
        self.product3 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 3',
            description='Descripción del producto 3',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )
        self.product4 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 4',
            description='Descripción del producto 4',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

        self.product5 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 5',
            description='Descripción del producto 5',
            show=False,
            stock_quantity=5,
            seller=self.user1,
        )

        self.product6 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 6',
            description='Descripción del producto 6',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

        self.product7 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 7',
            description='Descripción del producto 7',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

        self.product8 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 8',
            description='Descripción del producto 8',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

    def test_ok_add_product(self):
        image_content = b'contenido_de_imagen'
        image = SimpleUploadedFile("image.jpg", image_content, content_type="image/jpeg")
        data = {
            'product_type': 'P',
            'price': 200,
            'name': 'Producto 6',
            'description': 'Descripción del producto 6',
            'show': 'true',
            'stock_quantity': 5,
            'seller': self.user1,
            'file': image}
        response = self.client.post(reverse('add_product'), data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 201)
        response = self.client.get(reverse('products-list') + '?product_type=P')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 9)

    def test_wrong_add_product(self):
        self.product7 = Product.objects.create(
            product_type='P',
            price=200,
            name='Producto 7',
            description='Descripción del producto 7',
            show=True,
            stock_quantity=5,
            seller=self.user1,
        )

        image_content = b'contenido_de_imagen'
        image = SimpleUploadedFile("image.jpg", image_content, content_type="image/jpeg")
        data = {
            'product_type': 'P',
            'price': 200,
            'name': 'Producto 6',
            'description': 'Descripción del producto 6',
            'show': 'true',
            'stock_quantity': 5,
            'seller': self.user1,
            'file': image}
        response = self.client.post(reverse('add_product'), data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 400)

class ProductDeleteTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create(username='testuser',email='test34@example.com', password='password123', postal_code=12345)
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(
            product_type='P',
            price=10.0,
            name='Test Product',
            description='Test Description',
            show=True,
            stock_quantity=10,
            seller=self.user,
            imageRoute='',
            image='products/test_image.jpg',
            design=None
        )

    def test_delete_product(self):
        url = reverse('products-delete-product', kwargs={'pk': self.product.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_delete_product_unauthorized(self):
        unauthorized_user = CustomUser.objects.create(username='unauthorized',email='test35@example.com', password='password123', postal_code=12345)
        self.client.force_authenticate(user=unauthorized_user)
        url = reverse('products-delete-product', kwargs={'pk': self.product.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_not_owner(self):
        other_user = CustomUser.objects.create(username='otheruser',email='test36@example.com', password='password123', postal_code=12345)
        self.client.force_authenticate(user=other_user)
        url = reverse('products-delete-product', kwargs={'pk': self.product.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_not_authenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('products-delete-product', kwargs={'pk': self.product.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
