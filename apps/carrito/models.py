class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = 0
        self.carrito[producto_id] += cantidad
        self.guardar()

    def borrar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito.pop(producto_id)
        self.guardar()

    def sumar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito[producto_id] += 1
            self.guardar()

    def disminuir(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito[producto_id] -= 1
            if self.carrito[producto_id] <= 0:
                self.borrar(producto)
        self.guardar()

    def limpiar(self):
        self.session['carrito'] = {}
        self.guardar()

    def guardar(self):
        self.session.modified = True