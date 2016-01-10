from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import Cinephile


class CheckVoteMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        cinephile = Cinephile.objects.filter(actif=True, user=request.user)
        if cinephile.exists() and cinephile.first().pas_classes().exists():
            message = '<a href="%s">Tu n’as pas classé certains films !</a>' % reverse('cine:votes')
            messages.warning(request, mark_safe(message))
