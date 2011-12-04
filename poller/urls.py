from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('flowspy.poller.views',
                       ('^$', 'main'),
                       url('^a/message/existing$', 'message_existing', name='fetch-existing'),
                       url('^a/message/new$', 'message_new',name='fetch-new'),
                       url('^a/message/updates$', 'message_updates', name='fetch-updates'))

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)', 'django.views.static.serve',\
        {'document_root':  settings.STATIC_URL}),
)
