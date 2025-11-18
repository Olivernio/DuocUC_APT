# Generated manually to add Notification model

from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_favorite_products'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('message', models.TextField(max_length=500, verbose_name='Mensaje')),
                ('type', models.CharField(choices=[('ORDER_CREATED', 'Orden Creada'), ('ORDER_STATUS_CHANGED', 'Estado de Orden Cambiado'), ('REVIEW_CREATED', 'Reseña Creada'), ('GENERAL', 'General')], default='GENERAL', max_length=50, verbose_name='Tipo')),
                ('is_read', models.BooleanField(default=False, verbose_name='Leída')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Notificación',
                'verbose_name_plural': 'Notificaciones',
                'ordering': ['-created_at'],
            },
        ),
    ]

