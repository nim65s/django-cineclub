from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'app.views.previsions'),
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'home.html'}),
    url(r'^logout$', 'app.views.logout_view'),
    url(r'^films$', 'app.views.films'),
    url(r'^dispos$', 'app.views.dispos'),
    url(r'^votes$', 'app.views.votes'),
    url(r'^cinephiles$', 'app.views.cinephiles'),
    url(r'^faq$', 'app.views.faq'),
    url(r'^about$', 'app.views.about'),
    url(r'^profil$', 'app.views.profil'),
    url(r'^comms/(?P<slug>[^/]+)$', 'app.views.comms'),

    url(r'^admin/', include(admin.site.urls)),
)
