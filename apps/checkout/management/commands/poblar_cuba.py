from django.core.management.base import BaseCommand
from apps.checkout.models import Provincia, Municipio, Reparto, Tienda


class Command(BaseCommand):
    help = 'Pobla las provincias, municipios y repartos de Cuba con precios de envío'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando poblamiento de ubicaciones de Cuba...')
        
        # Datos de Cuba con precios de envío
        cuba_data = [
            {
                'provincia': 'La Habana',
                'precio_base': 200,
                'municipios': [
                    {
                        'nombre': 'Habana del Este',
                        'precio_adicional': 0,
                        'repartos': ['Alamar', 'Guanabacoa', 'Candelaria', 'Santa María del Mar']
                    },
                    {
                        'nombre': 'Plaza de la Revolución',
                        'precio_adicional': 0,
                        'repartos': ['Centro Habana', 'Plaza', 'Cerro', 'Camilo Cienfuegos']
                    },
                    {
                        'nombre': 'Habana Vieja',
                        'precio_adicional': 0,
                        'repartos': ['La Marina', 'San José', 'Casa Blanca', 'Troquises']
                    },
                    {
                        'nombre': 'Centro Habana',
                        'precio_adicional': 0,
                        'repartos': ['Cayo Hueso', 'Horcón', 'Portuelles']
                    },
                    {
                        'nombre': 'Cerro',
                        'precio_adicional': 0,
                        'repartos': ['Palatino', 'Mantilla', 'Ayesterán']
                    },
                    {
                        'nombre': 'Diez de Octubre',
                        'precio_adicional': 0,
                        'repartos': ['Placetas', 'Luyanó', 'Vista Alegre']
                    },
                    {
                        'nombre': 'San Miguel del Padrón',
                        'precio_adicional': 0,
                        'repartos': ['Güines', 'La Yuca', 'Zanja']
                    },
                    {
                        'nombre': 'Guanabacoa',
                        'precio_adicional': 0,
                        'repartos': ['Corralillo', 'Bacuranao']
                    },
                    {
                        'nombre': 'Marianao',
                        'precio_adicional': 0,
                        'repartos': ['Kholy', 'Managua', 'La Ceiba']
                    },
                    {
                        'nombre': 'Boyeros',
                        'precio_adicional': 0,
                        'repartos': ['Santiago de las Vegas', 'La Cuchilla']
                    },
                    {
                        'nombre': ' Arroyo Naranjo',
                        'precio_adicional': 0,
                        'repartos': ['Calle 100', 'Patricio', 'La Yuca']
                    },
                    {
                        'nombre': 'Cotorro',
                        'precio_adicional': 50,
                        'repartos': ['Acosta', 'Cali', 'Güira de Macurijes']
                    },
                    {
                        'nombre': 'San José de las Lajas',
                        'precio_adicional': 100,
                        'repartos': ['Bejucal', 'Jaragua', 'Capdevila']
                    },
                ]
            },
            {
                'provincia': 'Artemisa',
                'precio_base': 300,
                'municipios': [
                    {
                        'nombre': 'Artemisa',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Barrio Obrero', 'Baraguá']
                    },
                    {
                        'nombre': 'San Cristóbal',
                        'precio_adicional': 50,
                        'repartos': ['San Diego de los Baños', 'Los Palacios']
                    },
                    {
                        'nombre': 'Bahía Honda',
                        'precio_adicional': 100,
                        'repartos': ['Primavera', 'Los Terrones']
                    },
                    {
                        'nombre': 'Güira de Melena',
                        'precio_adicional': 50,
                        'repartos': ['Candelaria', 'Barranca']
                    },
                ]
            },
            {
                'provincia': 'Mayabeque',
                'precio_base': 350,
                'municipios': [
                    {
                        'nombre': 'San José de las Lajas',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'La Tumba']
                    },
                    {
                        'nombre': 'Güines',
                        'precio_adicional': 50,
                        'repartos': ['Mango', 'Jamaica']
                    },
                    {
                        'nombre': 'Madruga',
                        'precio_adicional': 100,
                        'repartos': ['La Juanita']
                    },
                    {
                        'nombre': 'Santa Cruz del Norte',
                        'precio_adicional': 150,
                        'repartos': ['Jibacoa', 'El Salado']
                    },
                ]
            },
            {
                'provincia': 'Matanzas',
                'precio_base': 400,
                'municipios': [
                    {
                        'nombre': 'Matanzas',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Versalles', 'Puerto']
                    },
                    {
                        'nombre': 'Cárdenas',
                        'precio_adicional': 50,
                        'repartos': ['Varadero', 'Jovellanos']
                    },
                    {
                        'nombre': 'Colón',
                        'precio_adicional': 100,
                        'repartos': ['Perico', 'Cienaga']
                    },
                    {
                        'nombre': 'Martí',
                        'precio_adicional': 150,
                        'repartos': ['Los Arabos']
                    },
                ]
            },
            {
                'provincia': 'Cienfuegos',
                'precio_base': 500,
                'municipios': [
                    {
                        'nombre': 'Cienfuegos',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Reina', 'Punta Gorda']
                    },
                    {
                        'nombre': 'Palmira',
                        'precio_adicional': 50,
                        'repartos': ['Rodas']
                    },
                    {
                        'nombre': 'Cruces',
                        'precio_adicional': 100,
                        'repartos': ['Cifuentes']
                    },
                ]
            },
            {
                'provincia': 'Villa Clara',
                'precio_base': 550,
                'municipios': [
                    {
                        'nombre': 'Santa Clara',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Capitán', 'Tropical']
                    },
                    {
                        'nombre': 'San Juan de los Remedios',
                        'precio_adicional': 100,
                        'repartos': ['Camajuaní']
                    },
                    {
                        'nombre': 'Placetas',
                        'precio_adicional': 150,
                        'repartos': ['Zulu']
                    },
                ]
            },
            {
                'provincia': 'Ciego de Ávila',
                'precio_base': 600,
                'municipios': [
                    {
                        'nombre': 'Ciego de Ávila',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'La Ceiba']
                    },
                    {
                        'nombre': 'Morón',
                        'precio_adicional': 50,
                        'repartos': ['Chambas']
                    },
                    {
                        'nombre': 'Baraguá',
                        'precio_adicional': 100,
                        'repartos': ['Cayo Coco']
                    },
                ]
            },
            {
                'provincia': 'Camagüey',
                'precio_base': 700,
                'municipios': [
                    {
                        'nombre': 'Camagüey',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Aguilar', 'La Popa']
                    },
                    {
                        'nombre': 'Vertientes',
                        'precio_adicional': 100,
                        'repartos': ['El Tisé']
                    },
                    {
                        'nombre': 'Sibanicú',
                        'precio_adicional': 150,
                        'repartos': ['Guáimaro']
                    },
                ]
            },
            {
                'provincia': 'Las Tunas',
                'precio_base': 750,
                'municipios': [
                    {
                        'nombre': 'Las Tunas',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Macagua']
                    },
                    {
                        'nombre': 'Puerto Padre',
                        'precio_adicional': 50,
                        'repartos': ['Manatí']
                    },
                    {
                        'nombre': 'Colombia',
                        'precio_adicional': 100,
                        'repartos': ['Jobos']
                    },
                ]
            },
            {
                'provincia': 'Holguín',
                'precio_base': 800,
                'municipios': [
                    {
                        'nombre': 'Holguín',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Plaza', 'La Güin']
                    },
                    {
                        'nombre': 'Gibara',
                        'precio_adicional': 100,
                        'repartos': ['Banes']
                    },
                    {
                        'nombre': 'Mayarí',
                        'precio_adicional': 150,
                        'repartos': ['Sagua de Tánamo']
                    },
                ]
            },
            {
                'provincia': 'Santiago de Cuba',
                'precio_base': 900,
                'municipios': [
                    {
                        'nombre': 'Santiago de Cuba',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Vista Alegre', 'Caridad']
                    },
                    {
                        'nombre': 'Palma Soriano',
                        'precio_adicional': 100,
                        'repartos': ['Contramaestre']
                    },
                    {
                        'nombre': 'San Luis',
                        'precio_adicional': 150,
                        'repartos': ['Tercer Frente']
                    },
                ]
            },
            {
                'provincia': 'Guantánamo',
                'precio_base': 1000,
                'municipios': [
                    {
                        'nombre': 'Guantánamo',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Barrio Josick']
                    },
                    {
                        'nombre': 'Baracoa',
                        'precio_adicional': 200,
                        'repartos': ['Maisí']
                    },
                    {
                        'nombre': 'Caimanera',
                        'precio_adicional': 150,
                        'repartos': ['El Salvador']
                    },
                ]
            },
            {
                'provincia': 'Pinar del Río',
                'precio_base': 350,
                'municipios': [
                    {
                        'nombre': 'Pinar del Río',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Hermanos Cruz', 'Ceferino']
                    },
                    {
                        'nombre': 'San Luis',
                        'precio_adicional': 50,
                        'repartos': ['Sandino']
                    },
                    {
                        'nombre': 'Consolación del Sur',
                        'precio_adicional': 100,
                        'repartos': ['Los Palacios']
                    },
                ]
            },
            {
                'provincia': 'Sancti Spíritus',
                'precio_base': 600,
                'municipios': [
                    {
                        'nombre': 'Sancti Spíritus',
                        'precio_adicional': 0,
                        'repartos': ['Centro', 'Bauta']
                    },
                    {
                        'nombre': 'Cabaiguán',
                        'precio_adicional': 50,
                        'repartos': ['Fomento']
                    },
                    {
                        'nombre': 'Trinidad',
                        'precio_adicional': 100,
                        'repartos': ['Sancti Spíritus']
                    },
                ]
            },
        ]

        # Limpiar datos existentes
        Reparto.objects.all().delete()
        Municipio.objects.all().delete()
        Provincia.objects.all().delete()
        
        self.stdout.write('Datos anteriores eliminados')

        # Crear datos
        for prov_data in cuba_data:
            provincia = Provincia.objects.create(
                nombre=prov_data['provincia'],
                precio_envio=prov_data['precio_base']
            )
            
            for mun_data in prov_data['municipios']:
                municipio = Municipio.objects.create(
                    provincia=provincia,
                    nombre=mun_data['nombre'],
                    precio_adicional=mun_data['precio_adicional']
                )
                
                for reparto_nombre in mun_data['repartos']:
                    Reparto.objects.create(
                        municipio=municipio,
                        nombre=reparto_nombre
                    )

        self.stdout.write(self.style.SUCCESS(f'Se crearon {Provincia.objects.count()} provincias'))
        self.stdout.write(self.style.SUCCESS(f'Se crearon {Municipio.objects.count()} municipios'))
        self.stdout.write(self.style.SUCCESS(f'Se crearon {Reparto.objects.count()} repartos'))

        # Crear tienda física por defecto
        if not Tienda.objects.exists():
            Tienda.objects.create(
                nombre='Tienda Principal',
                direccion='Calle 23 #105 entre Calles B y C, Vedado, Plaza de la Revolución, La Habana',
                telefono='+53 7 836 1234',
                activa=True
            )
            self.stdout.write(self.style.SUCCESS('Tienda física creada'))
        else:
            self.stdout.write('La tienda física ya existe')

        self.stdout.write(self.style.SUCCESS('Poblamiento completado exitosamente!'))