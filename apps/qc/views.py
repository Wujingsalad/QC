import datetime
import hashlib
import json
import random
import time

import requests
from django.db.models import Sum
from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qc.asset_load import TicketExcelSpecial, GTLoadExcel
from apps.qc.filter import ticket_filter, quality_filter
from apps.qc.models import Ticket, Quality, Qualitycase, Announcement, Recheck, RecheckLog
from apps.qc.serializer import Ticketloadserializer, Announcementserializer, Qualityinsertserializer, \
    Ticketunserializer, \
    Qualitycaseserializer, Selfticketserializer, Recheckserializer, Qualityserializer, Recheckunserializer, \
    Rechecklogserializer
from apps.qc.signal import recheck_history_signal

AppSecret = 'FDAE24F9BF944ADFB9A175A9FB3EADF6'
AppKey = '2dc6a6cb8597bb82a2eb73981bcefb57'
Headers = {'Content-Type': 'application/json;charset=UTF-8'}
tryingtimes = 0
status = {5: '未受理', 10: '受理中', 20: '已完结'}


class DataPagination(PageNumberPagination):
    page_size_query_description = 'pageSize'
    page_size_query_param = 'pageSize'
    page_size = 50


def encodemd5(appSecret, nonce):
    nowtime = int(time.time())
    md5 = hashlib.md5(nonce.encode('utf-8'))
    string = md5.hexdigest()
    content = appSecret + string + str(nowtime)
    try:
        sha = hashlib.sha1(content.encode('utf-8'))
        string = sha.hexdigest()
        return string, nowtime
    except:
        raise Exception


class TicketLoad(APIView):
    use_model = Ticket
    queryset = Ticket.objects.all()
    serializer_class = Ticketloadserializer

    def post(self, request, *args, **kwargs):
        fobj = request.FILES["file"]
        sheet = fobj.get_sheet()
        # 目的将任意输入日期格式，全部转换为str类型，datetime会被切割为dd/mm/yy格式字符串
        sheet.format(str)
        instance = TicketExcelSpecial(ser_class=self.serializer_class, class_name=self.use_model, sheet=sheet)
        instance.save_excel_to_db()
        return Response({})

    def put(self, request, *args, **kwargs):
        self.http_method_not_allowed(request, *args, **kwargs)


class ticket(viewsets.ModelViewSet):
    # pagination_class = DataPagination

    queryset = Ticket.objects.all()
    serializer_class = Ticketloadserializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ticket_filter
    filterset_fields = '__all__'

    def get_serializer_class(self):
        # 根据请求类型使用不同序列化器，读以外的操作使用反序列化器
        if self.action == 'list' or self.action == 'retrieve':
            return Ticketloadserializer

        return Ticketunserializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=True, url_path=r'detail')
    def DATA(self, request, *args, **kwargs):
        ticket_ins = self.get_object()
        data = {'ticketId': ticket_ins.ticketId}
        data = json.dumps(data)
        checksum, nowtime = encodemd5(AppSecret, data)
        res = requests.post(url="https://qiyukf.com/openapi/v2/ticket/new/detail?appKey=%s&time=%s&checksum=%s" % (
            AppKey, nowtime, checksum), data=data, headers=Headers, timeout=10)
        res = res.json()
        return Response(res['data'])

    @action(methods=['post'], detail=False, url_path=r'qualityinspection')
    def Qualityinspection(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(is_deleted=False, quality_status='待质检'))
        queryset.update(quality_status='未质检')
        serializer = Ticketloadserializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path=r'randominspection')
    def Randominspection(self, request, *args, **kwargs):
        proportion = self.request.query_params.get('proportion', 1)
        queryset = self.filter_queryset(self.get_queryset().filter(is_deleted=False, quality_status='待质检'))
        ids = random.sample(list(queryset.values_list('id', flat=True)), int(queryset.count() * eval(proportion)))
        queryset.filter(id__in=ids).update(quality_status='未质检')
        serializer = Ticketloadserializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True, url_path=r'beexample')
    def beexample(self, request, *args, **kwargs):
        ticket_ins = self.get_object()
        if not Qualitycase.objects.filter(ticket=ticket_ins.id).exists():
            obj = Qualitycase.objects.create(ticket=ticket_ins)
            return Response(Qualitycaseserializer(instance=obj).data)

        else:
            return Response('无法重复入库', status=400)

    @action(methods=['post'], detail=True, url_path=r'recheck')
    def recheck(self, request, *args, **kwargs):
        reason = request.data.get('reason', '')
        quality_ins = self.get_object()
        if not Recheck.objects.filter(ticket=quality_ins).exists():
            obj = Recheck.objects.create(ticket=quality_ins, user=self.request.user.name, reason=reason)
            return Response(Recheckserializer(instance=obj).data)

        else:
            obj = Recheck.objects.filter(ticket=quality_ins).first()
            if obj.status == '被拒绝':
                obj.status = '再次申请复检'
                obj.save()
                return Response(Recheckserializer(instance=obj).data)
            else:
                return Response('无法重复申诉', status=400)


class quality(viewsets.ModelViewSet):
    use_model = Quality
    queryset = Quality.objects.all()
    serializer_class = Qualityserializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = quality_filter
    filterset_fields = '__all__'

    @action(methods=['post'], detail=True, url_path=r'beexample')
    def beexample(self, request, *args, **kwargs):
        quality_ins = self.get_object()
        if not Qualitycase.objects.filter(quality=quality_ins.id).exists():
            obj = Qualitycase.objects.create(quality=quality_ins)
            return Response(Qualitycaseserializer(instance=obj).data)
        else:
            return Response('无法重复入库', status=400)

    @action(methods=['post'], detail=True, url_path=r'recheck')
    def recheck(self, request, *args, **kwargs):
        reason = request.data.get('reason', '')
        quality_ins = self.get_object()
        if not Recheck.objects.filter(quality=quality_ins).exists():
            obj = Recheck.objects.create(quality=quality_ins, user=self.request.user.name, reason=reason)
            return Response(Recheckserializer(instance=obj).data)
        else:
            obj = Recheck.objects.filter(ticket=quality_ins).first()
            if obj.status == '被拒绝':
                obj.status = '再次申请复检'
                obj.save()

                return Response(Recheckserializer(instance=obj).data)
            else:
                return Response('无法重复申诉', status=400)

    @action(methods=['post'], detail=False, url_path=r'qualityinspection')
    def Qualityinspection(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(is_deleted=False, quality_status='待质检'))
        queryset.update(quality_status='未质检')
        serializer = Qualityserializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path=r'randominspection')
    def Randominspection(self, request, *args, **kwargs):
        proportion = self.request.query_params.get('proportion', 1)
        queryset = self.filter_queryset(self.get_queryset().filter(is_deleted=False, quality_status='待质检'))
        ids = random.sample(list(queryset.values_list('id', flat=True)), int(queryset.count() * eval(proportion)))
        queryset.filter(id__in=ids).update(quality_status='未质检')
        serializer = Qualityserializer(queryset, many=True)
        return Response(serializer.data)


class session(viewsets.ModelViewSet):
    use_model = Ticket
    queryset = Ticket.objects.all()
    serializer_class = Ticketloadserializer

    @action(methods=['get'], detail=True, url_path=r'detail')
    def DATA(self, request, *args, **kwargs):
        ticket_ins = self.get_object()
        data = {'ticketId': ticket_ins.ticketId}
        data = json.dumps(data)
        checksum, nowtime = encodemd5(AppSecret, data)
        res = requests.post(url="https://qiyukf.com/openapi/v2/ticket/new/detail?appKey=%s&time=%s&checksum=%s" % (
            AppKey, nowtime, checksum), data=data, headers=Headers, timeout=10)
        res = res.json()
        return Response(res['data'])


class qualityLoad(APIView):
    use_model = Quality
    queryset = Quality.objects.all()
    serializer_class = Qualityinsertserializer
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        fobj = request.FILES["file"]
        sheet = fobj.get_sheet()
        # 目的将任意输入日期格式，全部转换为str类型，datetime会被切割为dd/mm/yy格式字符串
        sheet.format(str)
        instance = ITAssetExcelSpecial(ser_class=self.serializer_class, class_name=self.use_model, sheet=sheet)
        instance.save_excel_to_db()
        return Response({})

    def put(self, request, *args, **kwargs):
        self.http_method_not_allowed(request, *args, **kwargs)


class qualitycase(viewsets.ModelViewSet):
    use_model = Qualitycase
    queryset = Qualitycase.objects.all()
    serializer_class = Qualitycaseserializer


class recheck(viewsets.ModelViewSet):
    use_model = Recheck
    queryset = Recheck.objects.all()
    serializer_class = Recheckserializer

    def get_serializer_class(self):
        # 根据请求类型使用不同序列化器，读以外的操作使用反序列化器
        if self.action == 'update':
            return Recheckunserializer
        return Recheckserializer

    @action(methods=['post'], detail=True, url_path=r'accept')
    def accept(self, request, *args, **kwargs):
        recheck = self.get_object()
        comment = self.request.data.get('comment', '')
        recheck.handler = self.request.user.name
        recheck.comment = comment
        recheck.status = '复检接受'
        recheck.save()
        if Ticket.objects.filter(recheck=recheck).exists():
            obj = Ticket.objects.get(recheck=recheck)
        else:
            obj = Quality.objects.get(recheck=recheck)
        obj.basic_norm = 0
        obj.response = 0
        obj.desire = 0
        obj.expression = 0
        obj.accuracy = 0
        obj.integrity = 0
        obj.negative_feedback = 0
        obj.forbiddance_a = None
        obj.forbiddance_b = None
        obj.score = 0
        obj.problem = None
        obj.save()

        def create_signal(recheck_ins):
            print("发送信号")
            # 发送信号，将请求的IP地址和时间一并传递过去
            recheck_history_signal.send(create_signal, recheck=recheck)

        create_signal(self.get_object())
        return Response(Recheckserializer(instance=recheck).data)

    @action(methods=['post'], detail=True, url_path=r'cancel')
    def cancel(self, request, *args, **kwargs):
        recheck = self.get_object()
        comment = self.request.data.get('comment', '')
        recheck.handler = self.request.user.name
        recheck.comment = comment
        recheck.status = '被拒绝'
        recheck.save()

        def create_signal(recheck_ins):
            print("发送信号")
            # 发送信号，将请求的IP地址和时间一并传递过去
            recheck_history_signal.send(create_signal, recheck=recheck)

        create_signal(self.get_object())
        return Response(Recheckserializer(instance=recheck).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        def create_signal(recheck_ins):
            print("发送信号")
            # 发送信号，将请求的IP地址和时间一并传递过去
            recheck_history_signal.send(create_signal, recheck=recheck)

        create_signal(self.get_object())
        return Response(serializer.data)


class rechecklog(viewsets.ModelViewSet):
    use_model = RecheckLog
    queryset = RecheckLog.objects.all().order_by('-update_time')
    serializer_class = Rechecklogserializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = '__all__'
    pagination_class = None


class announcement(APIView):
    def get(self, request, *args, **kwargs):
        if not Announcement.objects.filter().exists():
            obj = Announcement.objects.create()
        else:
            obj = Announcement.objects.all().first()
        return Response(Announcementserializer(instance=obj).data)

    def post(self, request, *args, **kwargs):
        comment = self.request.data.get('comment', '')
        is_active = self.request.data.get('is_active', False)
        if not Announcement.objects.filter().exists():
            obj = Announcement.objects.create(comment=comment, is_active=is_active)
        else:
            obj = Announcement.objects.filter().update(comment=comment, is_active=is_active)
        return Response(Announcementserializer(instance=obj).data)


class total(APIView):
    def get(self, request, *args, **kwargs):
        start_time = self.request.query_params.get('start_time', datetime.datetime.utcfromtimestamp(0))
        end_time = self.request.query_params.get('end_time', datetime.datetime.now())
        user = self.request.user
        total_a = Ticket.objects.filter(inspect_time__gte=start_time, inspect_time__lte=end_time,
                                        holder=user.name).aggregate(
            total=Sum('basic_norm') + Sum('response') + Sum('response') + Sum('desire') + Sum('expression') + Sum(
                'accuracy') + Sum('integrity') + Sum('negative_feedback') + Sum('forbiddance_a') + Sum(
                'forbiddance_b')).get('total', 0)
        total_b = Quality.objects.filter(inspect_time__gte=start_time, inspect_time__lte=end_time,
                                         kefu=user.name).aggregate(
            total=Sum('basic_norm') + Sum('response') + Sum('response') + Sum('desire') + Sum('expression') + Sum(
                'accuracy') + Sum('integrity') + Sum('negative_feedback') + Sum('forbiddance_a') + Sum(
                'forbiddance_b')).get('total', 0)
        total_a = total_a if total_a else 0
        total_b = total_b if total_b else 0
        return Response({"total": total_a + total_b, "ticket": total_a, "quality": total_b})


class ITAssetExcelSpecial(GTLoadExcel):
    def get_instance(self):
        obj = None
        try:
            obj = self.class_name.objects.get(session=self.in_obj_data["session"])
        except:
            pass
        return obj


class selfticket(viewsets.ModelViewSet):
    # pagination_class = DataPagination

    queryset = Ticket.objects.all()
    serializer_class = Selfticketserializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ticket_filter
    filterset_fields = '__all__'

    def get_queryset(self):
        user = self.request.user.name
        queryset = Ticket.objects.filter(holder=user)
        return queryset

    @action(methods=['post'], detail=True, url_path=r'recheck')
    def recheck(self, request, *args, **kwargs):
        reason = self.request.data.get('reason')
        ticket_ins = self.get_object()
        if not Announcement.objects.filter(ticket=ticket_ins.id).exists():
            Announcement.objects.create(ticket=ticket_ins.id, reason=reason, user=self.request.user.name)
            return Response()

        else:
            return Response('无法重复申诉', status=400)

    @action(methods=['post'], detail=True, url_path=r'beexample')
    def beexample(self, request, *args, **kwargs):
        ticket_ins = self.get_object()
        if not Announcement.objects.filter(ticket=ticket_ins.id).exists():
            Announcement.objects.create(ticket=ticket_ins.id, user=self.request.user.name)
        else:
            return Response('无法重复申请', status=400)


class selfquality(viewsets.ModelViewSet):
    use_model = Quality
    queryset = Quality.objects.all()
    serializer_class = Announcementserializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = quality_filter
    filterset_fields = '__all__'

    def get_queryset(self):
        user = self.request.user.name
        queryset = Quality.objects.filter(kefu=user)
        return queryset

    @action(methods=['post'], detail=True, url_path=r'recheck')
    def recheck(self, request, *args, **kwargs):
        quality_ins = self.get_object()
        if not Qualitycase.objects.filter(quality=quality_ins.id).exists():
            Qualitycase.objects.create(quality=quality_ins.id, user=self.request.user.name)

        else:
            return Response('无法重复申诉')

    @action(methods=['post'], detail=True, url_path=r'beexample')
    def beexample(self, request, *args, **kwargs):
        quality_ins = self.get_object()
        if not Qualitycase.objects.filter(quality=quality_ins.id).exists():
            Qualitycase.objects.create(quality=quality_ins.id, user=self.request.user.name)
        else:
            return Response('无法重复申请')
