# Generated manually: seeds secciones editorial y colecciones y reordena el Home.

from django.db import migrations


def sembrar_nuevas_secciones(apps, schema_editor):
    HomeSeccion = apps.get_model('home', 'HomeSeccion')
    HomeEditorial = apps.get_model('home', 'HomeEditorial')
    HomeColeccion = apps.get_model('home', 'HomeColeccion')

    # Reordena las secciones existentes según la nueva estructura editorial.
    nuevos_ordenes = {
        'categorias': 10,
        'destacados': 20,
        'mas_vendidos': 30,
        'ofertas': 60,
        'nuevos': 50,
        'beneficios': 80,
    }
    for seccion in HomeSeccion.objects.all():
        if seccion.tipo in nuevos_ordenes:
            seccion.orden = nuevos_ordenes[seccion.tipo]
            seccion.save()

    # Sección editorial (Bloque revista).
    editorial, _ = HomeSeccion.objects.get_or_create(
        tipo='editorial',
        defaults={
            'titulo': 'La Selección del Mes',
            'subtitulo': 'Productos que están marcando tendencia',
            'orden': 40,
            'limite': 1,
            'activo': True,
        },
    )

    # Sección Descubre / Inspiración.
    colecciones, _ = HomeSeccion.objects.get_or_create(
        tipo='colecciones',
        defaults={
            'titulo': 'Descubre',
            'subtitulo': 'Explora lo que está en tendencia',
            'orden': 70,
            'limite': 3,
            'activo': True,
        },
    )

    # Contenido de ejemplo configurable desde el Admin (imágenes vacías).
    if not editorial.editoriales.exists():
        HomeEditorial.objects.create(
            seccion=editorial,
            titulo='La Selección del Mes',
            subtitulo='Productos que están marcando tendencia esta temporada. Descubre piezas únicas elegidas para ti.',
            texto_boton='Descubrir',
            enlace='/productos/',
            orden=0,
            activo=True,
        )

    colecciones_data = [
        ('Tecnología para tu día a día', 'Equipos y accesorios que simplifican tu rutina.', '/productos/'),
        ('Todo para tu hogar', 'Comodidad y estilo para cada espacio.', '/productos/'),
        ('Lo que está en tendencia', 'Los productos que todos están eligiendo.', '/productos/'),
    ]
    for orden, (titulo, descripcion, enlace) in enumerate(colecciones_data):
        HomeColeccion.objects.get_or_create(
            seccion=colecciones,
            titulo=titulo,
            defaults={
                'descripcion': descripcion,
                'enlace': enlace,
                'texto_boton': 'Descubrir',
                'orden': orden,
                'activo': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_homecoleccion_homeeditorial_delete_bannerintermedio_and_more'),
    ]

    operations = [
        migrations.RunPython(sembrar_nuevas_secciones, migrations.RunPython.noop),
    ]
