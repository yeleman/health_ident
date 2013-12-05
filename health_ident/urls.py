from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic.base import TemplateView

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^/?$',
        TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^browse/(?P<entity_slug>[a-zA-Z0-9]{3,4})/?$', 'health_ident.views.browser', name='browser_at'),
    url(r'^browse/?$', 'health_ident.views.browser', name='browser'),
    url(r'^map/?$', 'health_ident.views.map', name='map'),
    url(r'^admin/', include(admin.site.urls)),
)
