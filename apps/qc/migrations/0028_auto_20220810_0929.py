# Generated by Django 3.2.14 on 2022-08-10 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qc', '0027_auto_20220809_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='quality',
            name='finish_time',
            field=models.DateTimeField(default=None, null=True, verbose_name='会话结束时间'),
        ),
        migrations.AddField(
            model_name='quality',
            name='start_time',
            field=models.DateTimeField(default=None, null=True, verbose_name='会话开始时间'),
        ),
    ]
