from django.conf.urls.defaults import *

import views


urlpatterns = patterns('',
    url(r'$', views.all_fluffs, name='all_fluffs'),
   # url(r'^record/(?P<pk>[^/]+)/$', views.RecordView(), name='record'),
   # url(r'^record/(?P<lat>[^/d]+)/(?P<lng>[^/]+)/$', views.point_lookup, name='point_lookup'),
 )