from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from rapidsms_httprouter.urls import urlpatterns as router_urls
from ureport.urls import urlpatterns as ureport_urls
from contact.urls import urlpatterns as contact_urls
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_change
from generic.urls import urlpatterns as generic_urls
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^my-project/', include('my_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
    
    # RapidSMS core URLs
    url(r'^$', 'ureport.views.ureport_content', {'slug':'ureport_home','base_template':'ureport/three-square.html','num_columns':3,'create':True}, name='rapidsms-dashboard'),
    (r'^account/', include('rapidsms.urls.login_logout')),
    url(r'^$', 'ureport.views.index', name='rapidsms-dashboard'),    
    url('^accounts/login', 'rapidsms.views.login'),
    url('^accounts/logout', 'rapidsms.views.logout'),
    url('^accounts/change_password', login_required(password_change), {'template_name':'ureport/change_password.html', 'post_change_redirect':'/'}),
    # RapidSMS contrib app URLs
    (r'^ajax/', include('rapidsms.contrib.ajax.urls')),
    (r'^export/', include('rapidsms.contrib.export.urls')),
    (r'^httptester/', include('rapidsms.contrib.httptester.urls')),
    (r'^locations/', include('rapidsms.contrib.locations.urls')),
    (r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
    (r'^messaging/', include('rapidsms.contrib.messaging.urls')),
    (r'^scheduler/', include('rapidsms.contrib.scheduler.urls')),
    (r'^polls/', include('poll.urls')),
) + router_urls + ureport_urls + contact_urls + generic_urls

if settings.DEBUG:
    urlpatterns += patterns('',
        # helper URLs file that automatically serves the 'static' folder in
        # INSTALLED_APPS via the Django static media server (NOT for use in
        # production)
        (r'^', include('rapidsms.urls.static_media')),
    )

from rapidsms_httprouter.router import get_router
get_router(start_workers=True)