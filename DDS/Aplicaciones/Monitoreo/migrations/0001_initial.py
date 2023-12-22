# Generated by Django 5.0 on 2023-12-08 21:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Estacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
                ('ubicacion_geografica', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='LineaTransporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('tipo_transporte', models.CharField(choices=[('Subterraneo', 'Subterráneo'), ('Ferrocarril', 'Ferrocarril')], max_length=20)),
                ('estacion_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estacion_destino', to='Monitoreo.estacion')),
                ('estacion_origen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estacion_origen', to='Monitoreo.estacion')),
            ],
        ),
        migrations.CreateModel(
            name='PrestacionServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activo', models.BooleanField(default=True)),
                ('estacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Monitoreo.estacion')),
                ('linea_transporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Monitoreo.lineatransporte')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Monitoreo.servicio')),
            ],
        ),
    ]
