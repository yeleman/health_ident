from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.http import HttpResponse

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^/?$', 'health_ident.views.about', name='about'),
    url(r'^download/(.+)$', lambda r, x: HttpResponse(x), name='download'),
    url(r'^browse/(?P<entity_slug>[a-zA-Z0-9]{3,5})/?$', 'health_ident.views.browser', name='browser_at'),
    url(r'^browse/?$', 'health_ident.views.browser', name='browser'),
    url(r'^map/?$', 'health_ident.views.map', name='map'),
    url(r'^admin/', include(admin.site.urls)),
)
