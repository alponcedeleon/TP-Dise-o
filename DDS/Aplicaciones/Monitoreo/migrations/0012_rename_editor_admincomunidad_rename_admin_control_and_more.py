# Generated by Django 5.0 on 2023-12-28 01:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Monitoreo', '0011_role_admin_editor_viewer'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Editor',
            new_name='AdminComunidad',
        ),
        migrations.RenameModel(
            old_name='Admin',
            new_name='Control',
        ),
        migrations.RenameModel(
            old_name='Viewer',
            new_name='Miembro',
        ),
    ]
