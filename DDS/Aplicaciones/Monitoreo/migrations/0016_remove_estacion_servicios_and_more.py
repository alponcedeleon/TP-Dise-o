# Generated by Django 5.0 on 2024-02-21 02:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Monitoreo', '0015_remove_estacion_servicios_solicitudservicio'),
    ]

    operations = [
        
        migrations.AddField(
            model_name='solicitudservicio',
            name='comunidad',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Monitoreo.comunidad'),
            preserve_default=False,
        ),
    ]