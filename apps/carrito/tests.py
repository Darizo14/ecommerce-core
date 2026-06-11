from django.test import TestCase
from django.urls import reverse
from apps.products.models import Producto, Categoria


class CarritoTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Test')
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio='10.00',
            stock=10,
            categoria=self.categoria,
        )
        self.session = self.client.session
        self.cart_url = reverse('carrito:vista_carrito')
        self.add_url = reverse('carrito:agregar_carrito', args=[self.producto.id])
        self.api_url = reverse('carrito:obtener_carrito')

    def test_cart_page_loads_empty(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'carrito está vacío')

    def test_add_product_via_post(self):
        response = self.client.post(self.add_url, {'cantidad': 2})
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertIn(str(self.producto.id), session['carrito'])
        self.assertEqual(session['carrito'][str(self.producto.id)], 2)

    def test_add_product_via_post_ajax(self):
        response = self.client.post(
            self.add_url,
            {'cantidad': 3},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cantidad_total'], 3)

    def test_add_product_get_returns_405(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 405)

    def test_add_product_invalid_quantity(self):
        response = self.client.post(self.add_url, {'cantidad': -1})
        self.assertEqual(response.status_code, 302)

    def test_add_product_exceeds_stock(self):
        response = self.client.post(self.add_url, {'cantidad': 999})
        self.assertEqual(response.status_code, 302)

    def test_sumar_1(self):
        self.client.post(self.add_url, {'cantidad': 1})
        url = reverse('carrito:sumar_1', args=[self.producto.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session['carrito'][str(self.producto.id)], 2)

    def test_restar_1(self):
        self.client.post(self.add_url, {'cantidad': 5})
        url = reverse('carrito:restar_1', args=[self.producto.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session['carrito'][str(self.producto.id)], 4)

    def test_restar_1_removes_item_when_zero(self):
        self.client.post(self.add_url, {'cantidad': 1})
        url = reverse('carrito:restar_1', args=[self.producto.id])
        self.client.post(url)
        session = self.client.session
        self.assertNotIn(str(self.producto.id), session.get('carrito', {}))

    def test_eliminar_de_carrito(self):
        self.client.post(self.add_url, {'cantidad': 1})
        url = reverse('carrito:eliminar_de_carrito', args=[self.producto.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertNotIn(str(self.producto.id), session.get('carrito', {}))

    def test_cart_api(self):
        self.client.post(self.add_url, {'cantidad': 2})
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['cantidad_total'], 2)
        self.assertEqual(len(data['productos']), 1)

    def test_cart_cleanup_deleted_product(self):
        self.client.post(self.add_url, {'cantidad': 1})
        self.producto.delete()
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        session = self.client.session
        self.assertNotIn(str(self.producto.id), session.get('carrito', {}))
