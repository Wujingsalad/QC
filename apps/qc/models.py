from django.db import models

# Create your models here.
from django.db.models import Model

from utils.model import BaseModel, SoftModel


class Staff(BaseModel):
    """
    职位/岗位
    """
    staffId = models.IntegerField()
    realname = models.CharField(max_length=64)

    class Meta:
        verbose_name = '七鱼staff'
        app_label = 'qc'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self


class Ticket(BaseModel):
    """
    职位/岗位
    """
    title = models.CharField('名称', max_length=64)
    ticketId = models.IntegerField(unique=True)
    templateId = models.CharField(max_length=64, default=None, null=True)
    type = models.CharField(max_length=64, default=None, null=True)
    status = models.IntegerField(max_length=10, default=10, null=True)
    appName = models.CharField(max_length=64, default=None, null=True)
    holder = models.CharField(max_length=64, default=None, null=True)
    finish_time = models.DateTimeField(default=None, null=True)
    quality_status = models.CharField(max_length=32, default='待质检', null=True)
    inspector = models.CharField(max_length=36, verbose_name='质检人', default=None, null=True)
    inspect_time = models.DateTimeField(verbose_name='质检时间', default=None, null=True)
    basic_norm = models.FloatField(verbose_name='基本规范', default=None, null=True)
    response = models.FloatField(verbose_name='对用户的感谢做出回应', default=None, null=True)
    desire = models.FloatField(verbose_name='帮助意愿', default=None, null=True)
    expression = models.FloatField(verbose_name='表达能力', default=None, null=True)
    accuracy = models.FloatField(verbose_name='准确性', default=None, null=True)
    integrity = models.FloatField(verbose_name='完整性', default=None, null=True)
    negative_feedback = models.FloatField(verbose_name='非常不满意', default=None, null=True)
    forbiddance_a = models.FloatField(verbose_name='禁止一类', default=None, null=True)
    forbiddance_b = models.FloatField(verbose_name='禁止二类', default=None, null=True)
    score = models.FloatField(verbose_name='质检结果', default=None, null=True)
    comment = models.TextField(verbose_name='评语', default=None, null=True, blank=True)
    problem = models.CharField(verbose_name='严重问题', max_length=64, default=None, null=True, blank=True)

    class Meta:
        verbose_name = '工单'
        app_label = 'qc'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Session(BaseModel):
    """
    职位/岗位
    """
    name = models.CharField('名称', max_length=32, unique=True)
    description = models.CharField('描述', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '会话'
        app_label = 'qc'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Quality(BaseModel):
    session = models.CharField(max_length=24, verbose_name='会话ID', default=None, null=True)
    inspector = models.CharField(max_length=36, verbose_name='质检人', default=None, null=True)
    start_time = models.DateTimeField(verbose_name='会话开始时间', default=None, null=True, blank=True)
    finish_time = models.DateTimeField(verbose_name='会话结束时间', default=None, null=True, blank=True)
    inspect_time = models.DateTimeField(verbose_name='质检时间', default=None, null=True, blank=True)
    kefu = models.CharField(max_length=36, verbose_name='接待客服', default=None, null=True, blank=True)
    basic_norm = models.FloatField(verbose_name='基本规范', default=None, null=True, blank=True)
    response = models.FloatField(verbose_name='对用户的感谢做出回应', default=None, null=True, blank=True)
    desire = models.FloatField(verbose_name='帮助意愿', default=None, null=True, blank=True)
    expression = models.FloatField(verbose_name='表达能力', default=None, null=True, blank=True)
    accuracy = models.FloatField(verbose_name='准确性', default=None, null=True, blank=True)
    integrity = models.FloatField(verbose_name='完整性', default=None, null=True, blank=True)
    negative_feedback = models.FloatField(verbose_name='非常不满意', default=None, null=True, blank=True)
    forbiddance_a = models.FloatField(verbose_name='禁止一类', default=None, null=True, blank=True)
    forbiddance_b = models.FloatField(verbose_name='禁止二类', default=None, null=True, blank=True)
    score = models.FloatField(verbose_name='质检结果', default=None, null=True, blank=True)
    comment = models.TextField(verbose_name='评语', default=None, null=True, blank=True)
    quality_status = models.CharField(max_length=32, default='待质检', null=True, blank=True)
    problem = models.CharField(verbose_name='严重问题', max_length=64, default=None, null=True, blank=True)

    class Meta:
        verbose_name = '质检'
        app_label = 'qc'
        verbose_name_plural = verbose_name


class Qualitycase(SoftModel):
    ticket = models.ForeignKey(to=Ticket, null=True, default=None, on_delete=models.SET_NULL)
    quality = models.ForeignKey(to=Quality, null=True, default=None, on_delete=models.SET_NULL)
    comment = models.TextField(verbose_name='测评', null=True, default=None)

    class Meta:
        verbose_name = '案例'
        app_label = 'qc'
        verbose_name_plural = verbose_name


class Recheck(BaseModel):
    ticket = models.ForeignKey(to=Ticket, null=True, default=None, on_delete=models.SET_NULL)
    quality = models.ForeignKey(to=Quality, null=True, default=None, on_delete=models.SET_NULL)
    status = models.CharField(max_length=32, default='待审核')
    comment = models.TextField(verbose_name='评语', null=True, blank=True, default=None)
    reason = models.TextField(verbose_name='理由', null=True, blank=True, default=None)
    user = models.CharField(max_length=32, verbose_name='申请人')
    handler = models.CharField(max_length=32, verbose_name='处理人', default=None, null=True)

    class Meta:
        verbose_name = '复检'
        app_label = 'qc'
        verbose_name_plural = verbose_name


class RecheckLog(BaseModel):
    ticket = models.ForeignKey(to=Ticket, null=True, default=None, on_delete=models.SET_NULL)
    quality = models.ForeignKey(to=Quality, null=True, default=None, on_delete=models.SET_NULL)
    status = models.CharField(max_length=32, default='待审核')
    comment = models.TextField(verbose_name='评语', null=True, blank=True, default=None)
    reason = models.TextField(verbose_name='理由', null=True, blank=True, default=None)
    user = models.CharField(max_length=32, verbose_name='申请人')
    handler = models.CharField(max_length=32, verbose_name='处理人', default=None, null=True)

    class Meta:
        verbose_name = '复检'
        app_label = 'qc'
        verbose_name_plural = verbose_name


class Announcement(BaseModel):
    is_active = models.BooleanField(default=False)
    comment = models.TextField(verbose_name='内容', null=True, default=None)

    class Meta:
        verbose_name = '公告'
        app_label = 'qc'
        verbose_name_plural = verbose_name


class image(models.Model):
    """
        图片
    """
    image = models.ImageField(upload_to='static/images/%Y/%m/%d')
    name = models.CharField(default='', max_length=128)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image'
        app_label = 'qc'
