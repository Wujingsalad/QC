from django.conf.urls import url
from django.urls import path, include

from apps.qc.views import *

from rest_framework.routers import SimpleRouter


class StandardRouter(SimpleRouter):
    def __init__(self, trailing_slash='/?'):
        super(StandardRouter, self).__init__()
        self.trailing_slash = trailing_slash


app_name = 'qc'
router = StandardRouter()
router.register('ticket', ticket)
router.register('selfticket', selfticket)
router.register('selfqulity', selfquality)

router.register('quality', quality)
router.register('qualitycase', qualitycase)
router.register('recheck', recheck)
router.register('rechecklog', rechecklog)

urlpatterns = [
    url(r'qualityLoad', qualityLoad.as_view()),
    url(r'total', total.as_view()),
    url(r'announcement', announcement.as_view()),
    url(r'', include((router.urls, 'qc'))),

]
