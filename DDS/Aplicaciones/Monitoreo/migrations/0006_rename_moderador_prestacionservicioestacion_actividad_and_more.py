# Generated by Django 5.0 on 2024-02-06 01:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Monitoreo', '0005_rename_prestacionservicio_prestacionservicioestacion_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='prestacionservicioestacion',
            old_name='moderador',
            new_name='actividad',
        ),
        migrations.RenameField(
            model_name='prestacionserviciosucursal',
            old_name='moderador',
            new_name='actividad',
        ),
    ]
