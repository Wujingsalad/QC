# Generated by Django 3.2.14 on 2022-08-09 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qc', '0026_rechecklog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recheck',
            name='comment',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='评语'),
        ),
        migrations.AlterField(
            model_name='recheck',
            name='reason',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='理由'),
        ),
        migrations.AlterField(
            model_name='rechecklog',
            name='comment',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='评语'),
        ),
        migrations.AlterField(
            model_name='rechecklog',
            name='reason',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='理由'),
        ),
    ]
