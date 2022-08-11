import datetime

from django.dispatch import receiver, Signal

from apps.qc.serializer import  Recheckupdateserializer, Rechecklogunserializer

'''
    使用signal监控model变化
'''
curr_time = datetime.datetime.now()

recheck_history_signal = Signal(providing_args=['recheck'])


@receiver(recheck_history_signal)
def recheck_history(sender, **kwargs):
    recheck = kwargs['recheck']
    data = Recheckupdateserializer(instance=recheck).data
    data.pop('id')
    data.pop('update_time')
    serializer = Rechecklogunserializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    pass
