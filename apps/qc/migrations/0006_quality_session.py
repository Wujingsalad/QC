# Generated by Django 3.2.14 on 2022-07-26 09:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('qc', '0005_auto_20220725_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='创建时间', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改时间', verbose_name='修改时间')),
                ('is_deleted', models.BooleanField(default=False, help_text='删除标记', verbose_name='删除标记')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='名称')),
                ('description', models.CharField(blank=True, max_length=50, null=True, verbose_name='描述')),
            ],
            options={
                'verbose_name': '会话',
                'verbose_name_plural': '会话',
            },
        ),
        migrations.CreateModel(
            name='Quality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, help_text='创建时间', verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, help_text='修改时间', verbose_name='修改时间')),
                ('is_deleted', models.BooleanField(default=False, help_text='删除标记', verbose_name='删除标记')),
                ('basic_norm', models.IntegerField(verbose_name='基本规范')),
                ('response', models.IntegerField(verbose_name='对用户感谢做出回应')),
                ('desire', models.IntegerField(verbose_name='帮助意愿')),
                ('expression', models.IntegerField(verbose_name='表达能力')),
                ('accuracy', models.IntegerField(verbose_name='准确性')),
                ('integrity', models.IntegerField(verbose_name='完整性')),
                ('negative_feedback', models.IntegerField(verbose_name='非常不满意')),
                ('forbiddance', models.CharField(max_length=36, verbose_name='禁止类')),
                ('forbiddance_score', models.IntegerField(verbose_name='禁止类扣分')),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='qc.session')),
                ('ticket', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='qc.ticket')),
            ],
            options={
                'verbose_name': '质检',
                'verbose_name_plural': '质检',
            },
        ),
    ]
