from django.conf.urls import patterns, include, url
from visual.views import index
from visual.views import logfetch

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    ('^$', index),
    (r'^logfetch(.*)$', logfetch),

    (r'^img/(?P<path>.*)$','django.views.static.serve',{'document_root':'./visual/media/img'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',{'document_root':'./visual/media/js' }),
    (r'^css/(?P<path>.*)$','django.views.static.serve',{'document_root':'./visual/media/css'}),


    # Examples:
    # url(r'^$', 'visual.views.home', name='home'),
    # url(r'^visual/', include('visual.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
