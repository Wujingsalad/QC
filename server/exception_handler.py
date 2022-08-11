# import json
#
# from rest_framework.response import Response
# from rest_framework.views import exception_handler
#
#
# def custom_exception_handler(exc, context):
#     # Call REST framework's default exception handler first,
#     # to get the standard error response.
#     response = exception_handler(exc, context)
#
#     # Now add the HTTP status code to the response.
#     if response:
#         print(response.data)
#         if response.data.get('detail'):
#             response.data['message'] = response.data['detail']
#             response.data.pop('detail')
#         elif response.data.get('non_field_errors'):
#             response.data['message'] = response.data['non_field_errors']
#             response.data.pop('non_field_errors')
#         else:
#             data = '接口参数错误:%s' % str(response.data)
#             response.data = {'message': data}
#     return Response(response.data)
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
        拦截错误信息，返回指定错误信息
    """
    response = exception_handler(exc, context)
    if response:
        code = response.status_code
        try:
            detail = response.data.get('detail', None)
            non_field_errors = response.data.get('non_field_errors')
            # 异常响应
            if detail:
                return Response(status=code, data=detail)  # 根据status_code 来判断返回的异常的类型
            elif non_field_errors:
                return Response(status=code, data=non_field_errors)
            elif code == 403:
                return Response(status=code, data='认证失败')
            else:
                print(response.data)
                # return Response({'response': '接口参数错误', 'result': {}, 'code': '', 'tips': response.data})
                return Response(status=code, data=response.data)
        except:
            return Response(status=code, data=response.data)
