# Generated by Django 3.2.14 on 2022-07-28 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qc', '0019_recheck_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='qualitycase',
            name='status',
        ),
        migrations.RemoveField(
            model_name='qualitycase',
            name='user',
        ),
    ]
