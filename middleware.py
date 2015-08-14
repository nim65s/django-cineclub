from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


class CheckVoteMiddleware(object):
    def process_request(self, request):
        if request.user.groups.filter(name='cine').exists() and request.user.vote_set.filter(choix=9999, film__vu=False).exists():
                messages.warning(request, mark_safe('<a href="%s">Tu n’as pas classé certains films !</a>' % reverse('cine:votes')))
