#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para resetear las secuencias de PostgreSQL después de migrar datos
Este script corrige el problema de IntegrityError con llaves duplicadas
"""
import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from django.db import connection
from django.apps import apps

def reset_sequences():
    """
    Resetea todas las secuencias de PostgreSQL para que apunten al máximo ID + 1
    """
    print("=" * 60)
    print("RESETEANDO SECUENCIAS DE POSTGRESQL")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Obtener todas las tablas con modelos de Django
        models = apps.get_models()
        
        sequences_reset = []
        
        for model in models:
            if model._meta.abstract:
                continue
                
            table_name = model._meta.db_table
            pk_field = model._meta.pk
            
            # Solo procesar PKs numéricas (AutoField, BigAutoField, etc.)
            if not hasattr(pk_field, 'get_internal_type'):
                continue
                
            pk_type = pk_field.get_internal_type()
            if pk_type not in ['AutoField', 'BigAutoField', 'IntegerField', 'BigIntegerField']:
                continue
            
            pk_column = pk_field.column
            sequence_name = f"{table_name}_{pk_column}_seq"
            
            try:
                # Obtener el máximo ID actual
                cursor.execute(f'SELECT MAX("{pk_column}") FROM "{table_name}"')
                max_id = cursor.fetchone()[0]
                
                if max_id is None:
                    max_id = 0
                    print(f"  {table_name}: Sin datos, iniciando en 1")
                else:
                    print(f"  {table_name}: Maximo ID = {max_id}")
                
                # Verificar que la secuencia existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_sequences 
                        WHERE sequencename = %s AND schemaname = 'public'
                    )
                """, [sequence_name])
                
                sequence_exists = cursor.fetchone()[0]
                
                if sequence_exists:
                    # Resetear la secuencia al máximo ID + 1
                    # Usar true para que setval establezca el valor actual y sea usado
                    next_val = max_id + 1
                    cursor.execute(f"SELECT setval('{sequence_name}', {next_val}, true)")
                    set_val = cursor.fetchone()[0]
                    
                    sequences_reset.append({
                        'table': table_name,
                        'sequence': sequence_name,
                        'max_id': max_id,
                        'next_val': set_val
                    })
                    
                    print(f"    OK: Secuencia {sequence_name} reseteada. Proximo ID sera: {next_val}")
                else:
                    print(f"  {table_name}: Secuencia no existe, saltando")
                
            except Exception as e:
                # Si la tabla no existe o hay error, continuar
                error_msg = str(e)
                if 'does not exist' in error_msg or 'relation' in error_msg.lower() or 'no existe' in error_msg:
                    print(f"  {table_name}: Saltando (tabla o secuencia no existe)")
                else:
                    print(f"  {table_name}: Error - {error_msg}")
        
        # Hacer commit de los cambios
        connection.commit()
        
        print("\n" + "=" * 60)
        print(f"OK: {len(sequences_reset)} secuencias reseteadas exitosamente")
        print("=" * 60)
        
        return sequences_reset

def show_current_sequences():
    """
    Muestra el estado actual de las secuencias
    """
    print("\n" + "=" * 60)
    print("ESTADO ACTUAL DE SECUENCIAS")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Obtener todas las secuencias
        cursor.execute("""
            SELECT sequencename, last_value
            FROM pg_sequences
            WHERE schemaname = 'public'
            ORDER BY sequencename
        """)
        
        sequences = cursor.fetchall()
        
        if sequences:
            for seq_name, last_val in sequences:
                print(f"  {seq_name}: ultimo valor = {last_val}")
        else:
            print("  No se encontraron secuencias")

if __name__ == '__main__':
    try:
        # Verificar conexión
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"Conectado a: {version.split(',')[0]}\n")
        
        # Mostrar estado actual
        show_current_sequences()
        
        # Resetear secuencias
        reset_sequences()
        
        print("\nOK: Proceso completado. Ahora puedes ejecutar el servidor sin errores.")
        print("   Ejecuta: python manage.py runserver")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nVerifica:")
        print("  1. Que PostgreSQL este corriendo")
        print("  2. Que la base de datos 'petstorepos' exista")
        print("  3. Que las credenciales en .env sean correctas")
        sys.exit(1)
