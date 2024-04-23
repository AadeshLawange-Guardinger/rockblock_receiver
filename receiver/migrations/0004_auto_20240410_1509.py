# Generated by Django 5.0.3 on 2024-04-10 09:39

from django.db import migrations

def create_admin_user(apps, schema_editor):
    UserCredentials = apps.get_model('receiver', 'UserCredentials')
    UserCredentials.objects.create(username='Admin', password='Admin@123')

class Migration(migrations.Migration):

    dependencies = [
        ('receiver', '0003_usercredentials_alter_rockblockmessage_transmit_time'),
    ]

    operations = [
        migrations.RunPython(create_admin_user),
    ]
