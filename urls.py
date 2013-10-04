from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import *


urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^films$', films, name='films'),
    url(r'^dispos$', dispos, name='dispos'),
    url(r'^votes$', votes, name='votes'),
    url(r'^cinephiles$', cinephiles, name='cinephiles'),
    url(r'^faq$', TemplateView.as_view(template_name='cine/faq.html'), name="faq"),
    url(r'^about$', TemplateView.as_view(template_name='cine/about.html'), name="about"),
    url(r'^cinenim.ics$', ics, name='ics'),

    url(r'^comms/(?P<slug>[^/]+)$', comms, name='comms'),
)
