from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'health_ident.views.dashboard.dashboard', name='dashboard'),
    url(r'^admin/', include(admin.site.urls)),
)
