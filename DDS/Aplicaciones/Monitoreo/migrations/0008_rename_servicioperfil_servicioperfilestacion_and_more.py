# Generated by Django 5.0 on 2024-02-06 23:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Monitoreo', '0007_estacion_foto'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ServicioPerfil',
            new_name='ServicioPerfilEstacion',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='servicios',
        ),
        migrations.AlterField(
            model_name='servicioperfilestacion',
            name='servicio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Monitoreo.prestacionservicioestacion'),
        ),
        migrations.CreateModel(
            name='ServicioPerfilSucursal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Monitoreo.perfil')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Monitoreo.prestacionserviciosucursal')),
            ],
        ),
    ]