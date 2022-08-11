from rest_framework.fields import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from .models import Ticket
import logging

logger = logging.getLogger('log')


class GTLoadExcel():
    """
    django 处理excel数据导入
    将excel内容写入数据库时，需要注意以下两点
        1、默认唯一值是name，如果你的model不是时，需要重写get_instance方法
        2、默认删除id列内容，如果还有特殊处理，需要重写deal_special_field方法
            deal_special_field重新注意点
                a、需要同时删除id列时，加入父类id处理或者调用父类+自定义内容
                b、不需要删除id列时，完全重写
    """

    def __init__(self, ser_class, class_name, sheet):
        """
        初始化
        :param ser_class: model序化类
        :param class_name: 待操作model类名称
        :param sheet: 导入excel内容
        """
        self.ser_class = ser_class
        self.class_name = class_name
        self.sheet = sheet

    def save_excel_to_db(self):
        self.deal_excel()
        self.save_data()

    def deal_excel(self):
        """
        处理输入的excel并返回其内容列表
        :return: [{},{}]
        """
        self.data_list = self.deal_row_data()
        return self.data_list

    def save_data(self):
        # 保存到数据库
        for data in self.data_list:
            self.in_obj_data = data
            self.deal_special_field()
            obj = self.get_instance
            if obj:
                # update
                # ser = self.ser_class(obj, data=data)
                ser = self.ser_class(obj)
            else:
                # create
                ser = self.ser_class(data=data)
                if ser.is_valid():
                    ser.save()

                else:
                    logger.info(ser.errors)
                    raise

    def deal_special_field(self):
        """
        处理特殊 字段内容，如删除excel中主键内容，如id，防止输入主键内容意外覆盖正常内容
        :param data:
        :return:
        """
        # forbiddance_a = "forbiddance_a"
        # forbiddance_b = "forbiddance_b"
        # if self.in_obj_data[forbiddance_a] == '否':
        #     self.in_obj_data[forbiddance_a] = 0
        # if self.in_obj_data[forbiddance_b] == '否':
        #     self.in_obj_data[forbiddance_b] = 0

    @property
    def get_instance(self):
        """
        根据唯一字段获取对应对象
        :return:
        """
        obj = None
        try:
            obj = self.class_name.objects.get(name=self.in_obj_data["name"])
        except:
            pass

        return obj

    def deal_row_data(self):
        """
        处理导入excel中每一个行内容
        :return:
        """
        sheet = self.sheet
        header = sheet.row[0]
        attr_list = self.get_attr_map(header)
        post_data_list = []
        for idx in range(1, sheet.number_of_rows()):
            rdata = sheet.row[idx]
            tmp = dict(zip(attr_list, rdata))
            post_data_list.append(tmp)

        return post_data_list

    def get_attr_map(self, header):
        """
        建立表头和model字段对应关系
        :param header:
        :return:
        """
        field_dict = {field.verbose_name: field.name for field in self.class_name._meta.fields}
        attr_list = []
        for idx, head in enumerate(header):
            if field_dict.get(head):
                attr_list.append(field_dict[head])
            else:
                attr_list.append('')

        return attr_list


class TicketExcelSpecial(GTLoadExcel):
    def get_instance(self):
        obj = None
        try:
            obj = self.class_name.objects.get(code=self.in_obj_data["code"])
        except:
            pass

        return obj
