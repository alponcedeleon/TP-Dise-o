# Generated by Django 5.0 on 2024-02-21 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Monitoreo', '0018_remove_estacion_servicios_and_more'),
    ]

    operations = [
        
        migrations.AlterField(
            model_name='solicitudservicio',
            name='motivo',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
