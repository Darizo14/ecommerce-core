from django.db import models

class Carrito:                                                           #Para iniciar el carrito de compras en la sesión del usuario
    def __init__(self,request):                                          #Para acceder a la sesión del usuario y almacenar el carrito allí
        self.session = request.session                                   #Para acceder a la sesión del usuario
        carrito = self.session.get('carrito')                            #Si no hay un carrito en la sesión, se crea uno nuevo y se guarda en la sesión
        if not carrito:
            carrito = self.session['carrito'] = {}                       #El carrito se guarda como un diccionario en la sesión, donde la clave es el ID del producto y el valor es otro diccionario con los detalles del producto (nombre, precio, cantidad)
        self.carrito = carrito                                           #Para acceder al carrito como un atributo de la clase Carrito, lo que facilita su manipulación en otras partes del código (como en las vistas)

def agregar(self, producto):                                             #Para agregar un producto al carrito, se recibe un objeto producto (de la clase Producto) y se agrega al carrito utilizando su ID como clave. Si el producto ya está en el carrito, se incrementa la cantidad en lugar de agregarlo nuevamente.
    producto_id = str(producto.id)                                       #Se convierte el ID del producto a cadena para usarlo como clave en el diccionario del carrito, ya que las claves de los diccionarios deben ser de tipo string.
    if producto_id not in self.carrito:                                  #Si el producto no está en el carrito, se agrega con su nombre, precio y cantidad inicial de 1. Si ya está en el carrito, se incrementa la cantidad en 1.
        self.carrito[producto_id] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'cantidad': 1,
        }
    else:
        self.carrito[producto_id]['cantidad'] += 1
    self.guardar()

def borrar(self, producto):                                              #Para eliminar un producto del carrito, se recibe un objeto producto y se elimina del carrito utilizando su ID como clave. Si el producto no está en el carrito, no se hace nada.
    producto_id = str(producto.id)                                       #Se convierte el ID del producto a cadena para usarlo como clave en el diccionario del carrito.
    if producto_id in self.carrito:                                      #Si el producto está en el carrito, se elimina utilizando la función pop() del diccionario, que elimina la clave y su valor asociado.
        self.carrito.pop(producto_id)
    self.guardar()

def sumar(self, producto):
    product_id = str(producto.id)

    if product_id in self.cart:
        self.cart[product_id]['cantidad'] += 1
        self.save()
    

def disminuir(self, producto):                                           #Para disminuir la cantidad de un producto en el carrito, se recibe un objeto producto y se reduce su cantidad en 1. Si la cantidad llega a 0 o menos, se elimina el producto del carrito.
    producto_id = str(producto.id)                                       #Se convierte el ID del producto a cadena para usarlo como clave en el diccionario del carrito. 
    if producto_id in self.carrito:                                      #Si el producto está en el carrito, se reduce su cantidad en 1. Si la cantidad llega a 0 o menos, se elimina el producto del carrito utilizando la función borrar() definida anteriormente.
        self.carrito[producto_id]['cantidad'] -= 1
        if self.carrito[producto_id]['cantidad'] <= 0: 
            self.borrar(producto)
    self.guardar()

def limpiar(self):                                                       #Para limpiar el carrito, se elimina el carrito completo de la sesión del usuario utilizando la función pop() del diccionario de la sesión.
    self.session['carrito'] = {}                                         #El segundo argumento None se pasa para evitar un error si el carrito no existe en la sesión.
    self.guardar()

def guardar(self):
    self.session.modified = True

def total(self):
    return sum(item['precio'] * item['cantidad'] for item in self.carrito.values())