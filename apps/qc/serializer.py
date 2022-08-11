from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.qc.models import Ticket, Quality, Qualitycase, Announcement, Recheck, RecheckLog


class CurrentUser(object):
    def set_context(self, serializer_field):
        self.user_id = serializer_field.context['request'].user.name

    def __call__(self):
        return self.user_id


class Selfticketserializer(ModelSerializer):
    # holder = serializers.HiddenField(default=CurrentUser())

    class Meta:
        model = Ticket
        fields = "__all__"


class Ticketloadserializer(ModelSerializer):
    recheck_status = serializers.SerializerMethodField(read_only=True)

    def get_recheck_status(self, obj):
        # 自定义字段获取文章作者
        recheck = Recheck.objects.filter(ticket=obj)
        if recheck.exists():
            return recheck.first().status
        else:
            return '未申请'

    class Meta:
        model = Ticket
        fields = "__all__"


class Ticketunserializer(ModelSerializer):
    inspector = serializers.HiddenField(default=CurrentUser())

    class Meta:
        model = Ticket
        fields = "__all__"


class  Qualityserializer(ModelSerializer):
    recheck_status = serializers.SerializerMethodField(read_only=True)

    def get_recheck_status(self, obj):
        recheck = Recheck.objects.filter(quality=obj)
        if recheck.exists():
            return recheck.first().status
        else:
            return '未申请'

    class Meta:
        model = Quality
        fields = "__all__"


class Announcementserializer(ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"


class Qualityinsertserializer(ModelSerializer):
    inspect_time = serializers.DateTimeField(required=False, input_formats=['%d/%m/%y', 'iso-8601'])
    start_time = serializers.DateTimeField(required=False, input_formats=['%d/%m/%y', 'iso-8601'])
    finish_time = serializers.DateTimeField(required=False, input_formats=['%d/%m/%y', 'iso-8601'])

    class Meta:
        model = Quality
        fields = "__all__"


class Qualitycaseserializer(ModelSerializer):
    ticket = serializers.SerializerMethodField(read_only=True)
    quality = serializers.SerializerMethodField(read_only=True)

    def get_ticket(self, obj):
        # 自定义字段获取文章作者
        try:
            if obj.ticket:
                return Ticketloadserializer(instance=obj.ticket).data
            else:
                return {}
        except:
            return {}

    def get_quality(self, obj):
        # 自定义字段获取文章作者
        try:
            if obj.quality:
                return Announcementserializer(instance=obj.quality).data
            else:
                return {}
        except:
            return {}

    class Meta:
        model = Qualitycase
        fields = "__all__"


class Recheckserializer(ModelSerializer):
    ticket = serializers.SerializerMethodField(read_only=True)
    quality = serializers.SerializerMethodField(read_only=True)

    def get_ticket(self, obj):
        # 自定义字段获取文章作者
        try:
            if obj.ticket:
                return Ticketloadserializer(instance=obj.ticket).data
            else:
                return {}
        except:
            return {}

    def get_quality(self, obj):
        # 自定义字段获取文章作者
        try:
            if obj.quality:
                return Announcementserializer(instance=obj.quality).data
            else:
                return {}
        except:
            return {}

    class Meta:
        model = Recheck
        fields = "__all__"


class Recheckunserializer(ModelSerializer):
    ticket = serializers.SerializerMethodField(read_only=True)
    quality = serializers.SerializerMethodField(read_only=True)
    handler = serializers.HiddenField(default=CurrentUser())

    def get_ticket(self, obj):
        # 自定义字段获取文章作者
        try:
            if obj.ticket:
                return Ticketloadserializer(instance=obj.ticket).data
            else:
                return {}
        except:
            return {}

    def get_quality(self, obj):
        # 自定义字段获取文章作者
        try:
            if obj.quality:
                return Announcementserializer(instance=obj.quality).data
            else:
                return {}
        except:
            return {}

    class Meta:
        model = Recheck
        fields = "__all__"


class Recheckupdateserializer(ModelSerializer):
    class Meta:
        model = Recheck
        fields = "__all__"


class Rechecklogserializer(ModelSerializer):
    ticket = serializers.SerializerMethodField(read_only=True)
    quality = serializers.SerializerMethodField(read_only=True)

    def get_ticket(self, obj):
        # 自定义字段获取文章作者
        try:
            if obj.ticket:
                return Ticketloadserializer(instance=obj.ticket).data
            else:
                return {}
        except:
            return {}

    def get_quality(self, obj):
        # 自定义字段获取文章作者
        try:
            if obj.quality:
                return Announcementserializer(instance=obj.quality).data
            else:
                return {}
        except:
            return {}

    class Meta:
        model = RecheckLog
        fields = "__all__"


class Rechecklogunserializer(ModelSerializer):
    class Meta:
        model = RecheckLog
        fields = "__all__"


class Qualitycaseunserializer(ModelSerializer):
    user = serializers.HiddenField(default=CurrentUser())

    class Meta:
        model = Qualitycase
        fields = "__all__"
