# Generated by Django 3.2.14 on 2022-07-27 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qc', '0015_auto_20220727_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='comment',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='评语'),
        ),
    ]
