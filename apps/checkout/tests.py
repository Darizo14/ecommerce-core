from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from apps.products.models import Producto, Categoria
from apps.checkout.models import Provincia, Municipio, Reparto, Tienda, Pedido, DireccionEnvio


class CheckoutTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Test')
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio='10.00',
            stock=10,
            categoria=self.categoria,
        )
        self.provincia = Provincia.objects.create(nombre='La Habana', precio_envio=Decimal('5.00'))
        self.municipio = Municipio.objects.create(
            nombre='Plaza',
            provincia=self.provincia,
            precio_adicional=Decimal('1.00'),
        )
        self.reparto = Reparto.objects.create(nombre='Vedado', municipio=self.municipio)
        self.tienda = Tienda.objects.create(
            nombre='Tienda Principal',
            direccion='Calle 123, La Habana',
            telefono='12345678',
            activa=True,
        )
        self.checkout_url = reverse('checkout:index')

    def _setup_cart(self):
        session = self.client.session
        session['carrito'] = {str(self.producto.id): 2}
        session.save()

    def test_checkout_page_loads(self):
        self._setup_cart()
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)

    def test_checkout_with_empty_cart_redirects(self):
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 302)

    def test_step1_validation_empty_name(self):
        self._setup_cart()
        response = self.client.post(
            self.checkout_url,
            {'accion': 'siguiente', 'nombre': '', 'telefono': '12345678'},
        )
        self.assertContains(response, 'El nombre es obligatorio')

    def test_step1_validation_invalid_phone(self):
        self._setup_cart()
        response = self.client.post(
            self.checkout_url,
            {'accion': 'siguiente', 'nombre': 'Test User', 'telefono': '123'},
        )
        self.assertContains(response, 'Debe tener exactamente 8 dígitos')

    def test_step2_validation_no_delivery_method(self):
        self._setup_cart()
        session = self.client.session
        session['checkout_paso_esperado'] = 2
        session['checkout_data'] = {
            'nombre': 'Test User',
            'telefono': '12345678',
        }
        session.save()
        response = self.client.post(self.checkout_url, {'accion': 'siguiente', 'paso': 2})
        self.assertContains(response, 'Selecciona un método de entrega')

    def test_full_order_flow_store_pickup(self):
        self._setup_cart()
        session = self.client.session
        session['checkout_paso_esperado'] = 1
        session.save()

        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'nombre': 'Test User',
            'telefono': '12345678',
        })
        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'metodo_entrega': 'tienda',
            'tienda_id': self.tienda.id,
        })
        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'metodo_pago': 'efectivo',
        })
        response = self.client.post(self.checkout_url, {'accion': 'confirmar'})
        self.assertIn(response.status_code, [200, 302])

    def test_full_order_flow_delivery(self):
        self._setup_cart()
        session = self.client.session
        session['checkout_paso_esperado'] = 1
        session.save()

        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'nombre': 'Test User',
            'telefono': '12345678',
        })
        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'metodo_entrega': 'mensajeria',
            'provincia': self.provincia.id,
            'municipio': self.municipio.id,
            'reparto': self.reparto.id,
            'direccion': 'Calle 456 #789',
        })
        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'metodo_pago': 'efectivo',
        })
        response = self.client.post(self.checkout_url, {'accion': 'confirmar'})
        self.assertIn(response.status_code, [200, 302])

    def test_api_municipios(self):
        url = reverse('checkout:api_municipios')
        response = self.client.get(url, {'provincia_id': self.provincia.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['municipios']), 1)
        self.assertEqual(data['municipios'][0]['nombre'], 'Plaza')

    def test_api_repartos(self):
        url = reverse('checkout:api_repartos')
        response = self.client.get(url, {'municipio_id': self.municipio.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['repartos']), 1)
        self.assertEqual(data['repartos'][0]['nombre'], 'Vedado')

    def test_confirmation_page_with_uuid(self):
        self._setup_cart()
        session = self.client.session
        session['checkout_paso_esperado'] = 1
        session.save()

        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'nombre': 'Test User',
            'telefono': '12345678',
        })
        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'metodo_entrega': 'tienda',
            'tienda_id': self.tienda.id,
        })
        self.client.post(self.checkout_url, {
            'accion': 'siguiente',
            'metodo_pago': 'efectivo',
        })
        response = self.client.post(self.checkout_url, {'accion': 'confirmar'})

        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            confirm_url = response['Location']
        self.assertIn('/confirmacion/', confirm_url)
        self.assertNotIn('uuid=', confirm_url)
