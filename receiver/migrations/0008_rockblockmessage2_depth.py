# Generated by Django 5.0.3 on 2024-09-10 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receiver', '0007_rockblockmessagedepth'),
    ]

    operations = [
        migrations.AddField(
            model_name='rockblockmessage2',
            name='depth',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
