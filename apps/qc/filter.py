from django_filters import rest_framework as filters

from apps.qc.models import Ticket, Quality


class ticket_filter(filters.FilterSet):
    """
        玩家筛选
    """
    start_time = filters.DateFilter(field_name='create_time', lookup_expr='gte', help_text="起始时间")
    end_time = filters.DateFilter(field_name='create_time', lookup_expr='lte', help_text="结束时间")

    class Meta:
        model = Ticket
        fields = '__all__'


class quality_filter(filters.FilterSet):
    """
        玩家筛选
    """
    start_time = filters.DateFilter(field_name='inspect_time', lookup_expr='gte', help_text="起始时间")
    end_time = filters.DateFilter(field_name='inspect_time', lookup_expr='lte', help_text="结束时间")

    class Meta:
        model = Quality
        fields = '__all__'
