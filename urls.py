from django.conf.urls import patterns, url
from cine.views import *


urlpatterns = patterns('',
    url(r'^$', previsions, name='home'),
    url(r'^films$', films, name='films'),
    url(r'^dispos$', dispos, name='dispos'),
    url(r'^votes$', votes, name='votes'),
    url(r'^cinephiles$', cinephiles, name='cinephiles'),
    url(r'^profil$', profil, name='profil'),
    url(r'^faq$', faq, name='faq'),
    #url(r'^about$', 'about'),

    url(r'^comms/(?P<slug>[^/]+)$', comms, name='comms'),
)
