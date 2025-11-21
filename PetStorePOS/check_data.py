#!/usr/bin/env python
"""Script para verificar datos en SQLite y PostgreSQL"""
import sqlite3
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
import django
django.setup()

from django.contrib.auth.models import User
from catalog.models import Product
from orders.models import Order
from cart.models import Cart
from adoption.models import Mascota

print("=" * 60)
print("COMPARACIÓN DE DATOS: SQLite vs PostgreSQL")
print("=" * 60)

# Verificar SQLite
print("\n📦 DATOS EN SQLITE:")
try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    tables_to_check = [
        ('auth_user', 'Usuarios'),
        ('catalog_product', 'Productos'),
        ('orders_order', 'Órdenes'),
        ('cart_cart', 'Carritos'),
        ('adoption_mascota', 'Mascotas'),
        ('accounts_userprofile', 'Perfiles de Usuario'),
        ('catalog_productreview', 'Reseñas'),
        ('orders_orderitem', 'Items de Orden'),
    ]
    
    sqlite_counts = {}
    for table, label in tables_to_check:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            sqlite_counts[table] = count
            print(f"  {label}: {count}")
        except sqlite3.OperationalError as e:
            sqlite_counts[table] = 0
            print(f"  {label}: 0 (tabla no existe o vacía)")
    
    conn.close()
except Exception as e:
    print(f"Error al conectar a SQLite: {e}")
    sqlite_counts = {}

# Verificar PostgreSQL
print("\n🐘 DATOS EN POSTGRESQL:")
try:
    pg_counts = {
        'auth_user': User.objects.count(),
        'catalog_product': Product.objects.count(),
        'orders_order': Order.objects.count(),
        'cart_cart': Cart.objects.count(),
        'adoption_mascota': Mascota.objects.count(),
    }
    
    # Agregar más modelos
    from accounts.models import UserProfile
    from catalog.models import ProductReview
    from orders.models import OrderItem
    
    pg_counts['accounts_userprofile'] = UserProfile.objects.count()
    pg_counts['catalog_productreview'] = ProductReview.objects.count()
    pg_counts['orders_orderitem'] = OrderItem.objects.count()
    
    labels = {
        'auth_user': 'Usuarios',
        'catalog_product': 'Productos',
        'orders_order': 'Órdenes',
        'cart_cart': 'Carritos',
        'adoption_mascota': 'Mascotas',
        'accounts_userprofile': 'Perfiles de Usuario',
        'catalog_productreview': 'Reseñas',
        'orders_orderitem': 'Items de Orden',
    }
    
    for table, count in pg_counts.items():
        label = labels.get(table, table)
        print(f"  {label}: {count}")
        
except Exception as e:
    print(f"Error al conectar a PostgreSQL: {e}")
    pg_counts = {}

# Comparación
print("\n" + "=" * 60)
print("RESUMEN:")
print("=" * 60)

total_sqlite = sum(sqlite_counts.values())
total_pg = sum(pg_counts.values())

print(f"Total de registros en SQLite: {total_sqlite}")
print(f"Total de registros en PostgreSQL: {total_pg}")

if total_pg == 0 and total_sqlite > 0:
    print("\n⚠️  LOS DATOS NO HAN SIDO MIGRADOS TODAVÍA")
    print("Necesitas migrar los datos desde SQLite a PostgreSQL")
    print("\nOpciones:")
    print("1. Usar DBeaver: Database → Tools → Database Migration")
    print("2. Usar Django: python manage.py loaddata datadump_sqlite.json")
elif total_pg > 0 and total_pg == total_sqlite:
    print("\n✅ Los datos están migrados correctamente")
elif total_pg > 0 and total_pg < total_sqlite:
    print(f"\n⚠️  Solo se migraron {total_pg} de {total_sqlite} registros")
else:
    print("\n✅ PostgreSQL está listo para recibir datos")

