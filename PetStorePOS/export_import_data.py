#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para exportar datos de SQLite e importarlos a PostgreSQL
"""
import os
import sys
import json

# Configurar encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')

print("=" * 60)
print("MIGRACIÓN DE DATOS: SQLite → PostgreSQL")
print("=" * 60)

# Paso 1: Cambiar a SQLite temporalmente
print("\n1. Cambiando a SQLite para exportar datos...")
from djangocrud import settings

# Guardar configuración original
original_db = settings.DATABASES['default'].copy()

# Cambiar a SQLite
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': str(settings.BASE_DIR / 'db.sqlite3'),
}

import django
django.setup()

# Exportar datos
print("2. Exportando datos de SQLite...")
from django.core.management import call_command
from io import StringIO

output = StringIO()
try:
    call_command(
        'dumpdata',
        '--exclude', 'orders.coupon',
        '--exclude', 'orders.ordercoupon',
        '--exclude', 'auth.permission',
        '--exclude', 'contenttypes',
        '--natural-foreign',
        '--natural-primary',
        '--indent', '2',
        stdout=output
    )
    data_json = output.getvalue()
    
    # Guardar en archivo
    with open('datadump_export.json', 'w', encoding='utf-8') as f:
        f.write(data_json)
    
    # Verificar
    data = json.loads(data_json)
    print(f"   ✅ Exportados {len(data)} objetos")
    
    # Contar por modelo
    models = {}
    for item in data:
        model = item['model']
        models[model] = models.get(model, 0) + 1
    
    print("\n   Desglose:")
    for model, count in sorted(models.items()):
        print(f"     - {model}: {count}")
    
except Exception as e:
    print(f"   ❌ Error al exportar: {e}")
    sys.exit(1)

# Paso 2: Cambiar a PostgreSQL
print("\n3. Cambiando a PostgreSQL...")
settings.DATABASES['default'] = original_db

# Forzar recarga de conexiones
from django.db import connections
connections.close_all()

import django
django.setup()

# Verificar conexión
print("4. Verificando conexión a PostgreSQL...")
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ Conectado a: {version.split(',')[0]}")
except Exception as e:
    print(f"   ❌ Error de conexión: {e}")
    sys.exit(1)

# Paso 3: Importar datos
print("\n5. Importando datos a PostgreSQL...")
try:
    call_command('loaddata', 'datadump_export.json', verbosity=2)
    print("   ✅ Datos importados exitosamente")
except Exception as e:
    print(f"   ❌ Error al importar: {e}")
    print("\n   Intenta usar DBeaver para migrar los datos manualmente")
    sys.exit(1)

# Paso 4: Verificar
print("\n6. Verificando datos migrados...")
from django.contrib.auth.models import User
from catalog.models import Product
from orders.models import Order
from cart.models import Cart
from adoption.models import Mascota

counts = {
    'Usuarios': User.objects.count(),
    'Productos': Product.objects.count(),
    'Órdenes': Order.objects.count(),
    'Carritos': Cart.objects.count(),
    'Mascotas': Mascota.objects.count(),
}

print("\n   Datos en PostgreSQL:")
for label, count in counts.items():
    print(f"     - {label}: {count}")

total = sum(counts.values())
print(f"\n   Total: {total} registros")

if total > 1:
    print("\n" + "=" * 60)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("⚠️  La migración no importó datos suficientes")
    print("Considera usar DBeaver para migrar manualmente")
    print("=" * 60)

