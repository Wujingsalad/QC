import datetime
import hashlib
import json
import math
import re
import time

import requests
from celery import shared_task

from apps.qc.models import Ticket

AppSecret = 'FDAE24F9BF944ADFB9A175A9FB3EADF6'
AppKey = '2dc6a6cb8597bb82a2eb73981bcefb57'
Headers = {'Content-Type': 'application/json;charset=UTF-8'}


def day_time(x):
    # 将python的datetime转换为unix时间戳
    days = datetime.date.today() + datetime.timedelta(days=x)
    # 将两个表达式链接，就是今天+-天数
    times = int(time.mktime(days.timetuple()) * 1000)
    # 将得到的数值转化为时间戳并返回
    return times


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


def get_staff():
    data = {}
    staff_dict = {}
    data["status"] = 1
    data = json.dumps(data)
    checksum, nowtime = encodemd5(AppSecret, data)
    res = requests.post(url="https://qiyukf.com/openapi/v2/staff/list?appKey=%s&time=%s&checksum=%s" % (
        AppKey, nowtime, checksum), data=data, headers=Headers, timeout=10)
    res = res.json()
    if res['code'] == 200:
        if 'message' in res:
            res['message'] = json.loads(res['message'])
    staff_list = res['message']
    for staff in staff_list:
        staff_dict[staff['id']] = staff['realname']
    return staff_dict


def get_ticketId(staff_dict):
    data = {'staffId': 1790092, "filterId": 6151760}
    data = json.dumps(data)
    checksum, nowtime = encodemd5(AppSecret, data)
    url = 'https://qiyukf.com/openapi/v2/ticket/filter/count?appKey=%s&time=%s&checksum=%s' % (
        AppKey, nowtime, checksum)
    res = requests.post(url=url, data=data, headers=Headers).json()
    if res['code'] == 200:
        if 'message' in res:
            res['message'] = json.loads(res['message'])
    count = res['message']
    print(count)
    x = count / 50
    offset_count = math.ceil(x)
    print(offset_count)
    ticketlist = {'工单id': [], '创建时间': [], '完结时间': [], '受理人': []}
    for i in range(0, offset_count):
        data = {'staffId': 1790092, "filterId": 6151760, 'offset': i * 50, 'limit': 50}
        data = json.dumps(data)
        checksum, nowtime = encodemd5(AppSecret, data)
        url = 'https://qiyukf.com/openapi/v2/ticket/list?appKey=%s&time=%s&checksum=%s' % (
            AppKey, nowtime, checksum)
        res = requests.post(url=url, data=data, headers=Headers).json()
        if res['code'] == 200:
            if 'message' in res:
                res['message'] = json.loads(res['message'])
        tickets = res['message']['tickets']
        for ticket in tickets:
            try:
                ip = re.split(r',', ticket['content'])[0]
                location = re.split(r',', ticket['content'])[1]
            except:
                ip = ''
                location = ''
            if not Ticket.objects.filter(ticketId=ticket['id']).exists():
                print(ticket)
                Ticket.objects.create(ticketId=ticket['id'], create_time=time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                       time.localtime(ticket[
                                                                                                          'createTime'] / 1000)),
                                      appName=staff_dict[ticket['staffId']] if ticket['staffId'] else '',
                                      title=ticket['title'] if ticket['title'] else '',
                                      holder=staff_dict[ticket['holderId']] if ticket['holderId'] else '',)


@shared_task(max_retries=5, default_retry_delay=1 * 6)
# 使用session创建session对象，时刻保持相应状态
def get_data():
    get_ticketId(get_staff())
