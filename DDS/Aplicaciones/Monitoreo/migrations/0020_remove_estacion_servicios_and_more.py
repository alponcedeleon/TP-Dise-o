# Generated by Django 5.0 on 2024-02-22 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Monitoreo', '0019_remove_estacion_servicios_and_more'),
    ]

    operations = [
        
        migrations.AddField(
            model_name='solicitudservicio',
            name='estaciones',
            field=models.ManyToManyField(blank=True, to='Monitoreo.estacion'),
        ),
        migrations.AddField(
            model_name='solicitudservicio',
            name='sucursales',
            field=models.ManyToManyField(blank=True, to='Monitoreo.sucursal'),
        ),
    ]