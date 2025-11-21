#!/usr/bin/env python
"""
Script de ayuda para migrar de SQLite a PostgreSQL
Este script ayuda a exportar datos de SQLite y preparar la migración
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
import json

def export_sqlite_data():
    """Exporta todos los datos de SQLite a un archivo JSON"""
    print("=" * 60)
    print("Exportando datos de SQLite...")
    print("=" * 60)
    
    # Cambiar temporalmente a SQLite
    original_db = settings.DATABASES['default'].copy()
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(settings.BASE_DIR, 'db.sqlite3'),
    }
    
    try:
        output_file = 'datadump_sqlite.json'
        print(f"Exportando datos a {output_file}...")
        
        # Exportar datos excluyendo algunas tablas del sistema
        call_command(
            'dumpdata',
            '--exclude', 'auth.permission',
            '--exclude', 'contenttypes',
            '--natural-foreign',
            '--natural-primary',
            output=output_file,
            indent=2
        )
        
        print(f"✓ Datos exportados exitosamente a {output_file}")
        
        # Mostrar estadísticas
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"\nTotal de objetos exportados: {len(data)}")
            
            # Contar por tipo
            counts = {}
            for item in data:
                model = item['model']
                counts[model] = counts.get(model, 0) + 1
            
            print("\nDesglose por modelo:")
            for model, count in sorted(counts.items()):
                print(f"  - {model}: {count}")
        
        return output_file
        
    except Exception as e:
        print(f"✗ Error al exportar datos: {e}")
        return None
    finally:
        # Restaurar configuración original
        settings.DATABASES['default'] = original_db

def check_postgresql_connection():
    """Verifica la conexión a PostgreSQL"""
    print("\n" + "=" * 60)
    print("Verificando conexión a PostgreSQL...")
    print("=" * 60)
    
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✓ Conexión exitosa a PostgreSQL")
            print(f"  Versión: {version.split(',')[0]}")
            
            # Verificar base de datos
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(f"  Base de datos: {db_name}")
            
            return True
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        print("\nVerifica:")
        print("  1. Que PostgreSQL esté corriendo")
        print("  2. Que la base de datos 'petstorepos' exista")
        print("  3. Que las credenciales en .env sean correctas")
        print("  4. Usuario: postgres, Password: 123123")
        return False

def import_to_postgresql(dump_file):
    """Importa datos a PostgreSQL"""
    print("\n" + "=" * 60)
    print("Importando datos a PostgreSQL...")
    print("=" * 60)
    
    if not os.path.exists(dump_file):
        print(f"✗ Archivo {dump_file} no encontrado")
        return False
    
    try:
        print(f"Importando desde {dump_file}...")
        call_command('loaddata', dump_file, verbosity=2)
        print("✓ Datos importados exitosamente")
        return True
    except Exception as e:
        print(f"✗ Error al importar datos: {e}")
        return False

def show_instructions():
    """Muestra instrucciones de uso"""
    print("=" * 60)
    print("MIGRACIÓN DE SQLITE A POSTGRESQL")
    print("=" * 60)
    print("\nEste script te ayudará a migrar los datos.")
    print("\nPasos recomendados:")
    print("1. Asegúrate de tener PostgreSQL instalado y corriendo")
    print("2. Crea la base de datos 'petstorepos' en PostgreSQL")
    print("3. Configura el archivo .env con tus credenciales")
    print("4. Ejecuta las migraciones de Django:")
    print("   python manage.py migrate")
    print("5. Ejecuta este script para exportar datos de SQLite")
    print("6. Cambia la configuración a PostgreSQL en settings.py")
    print("7. Ejecuta las migraciones nuevamente")
    print("8. Importa los datos usando:")
    print("   python manage.py loaddata datadump_sqlite.json")
    print("\n" + "=" * 60)

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'export':
            export_sqlite_data()
        elif command == 'check':
            check_postgresql_connection()
        elif command == 'import':
            dump_file = sys.argv[2] if len(sys.argv) > 2 else 'datadump_sqlite.json'
            import_to_postgresql(dump_file)
        elif command == 'full':
            # Proceso completo
            if export_sqlite_data():
                if check_postgresql_connection():
                    print("\n¿Deseas importar los datos ahora? (s/n): ", end='')
                    response = input().lower()
                    if response == 's':
                        import_to_postgresql('datadump_sqlite.json')
        else:
            print(f"Comando desconocido: {command}")
            print("Comandos disponibles: export, check, import, full")
    else:
        show_instructions()
        print("\nUso:")
        print("  python migrate_to_postgresql.py export  - Exportar datos de SQLite")
        print("  python migrate_to_postgresql.py check   - Verificar conexión PostgreSQL")
        print("  python migrate_to_postgresql.py import  - Importar datos a PostgreSQL")
        print("  python migrate_to_postgresql.py full    - Proceso completo guiado")

if __name__ == '__main__':
    main()

