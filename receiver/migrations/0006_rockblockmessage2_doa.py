# Generated by Django 5.0.3 on 2024-04-23 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receiver', '0005_rockblockmessage2'),
    ]

    operations = [
        migrations.AddField(
            model_name='rockblockmessage2',
            name='doa',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]