from cine.models import DispoToWatch
from django import template
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from perso.templatetags.perso_extra import url_get

register = template.Library()


@register.simple_tag
def films_url(request, key, value):
    return "%s%s" % (reverse('cinenim:films'), url_get(request, key, value))


@register.simple_tag
def dispo_buttons(user, soiree):
    if not user.groups.filter(name='cine').exists():
        return ''
    dtw, created = DispoToWatch.objects.get_or_create(soiree=soiree, cinephile=user)
    if created:
        mail_admins('DispoToWatch Créée sans raisons', '%s / %s' % (soiree, user))
    return """
    <div class="btn-group" data-toggle="buttons">
        <label class="btn %(O)s btn-success" onclick="Dajaxice.cine.dispo(Dajax.process,{'date':'%(date)s','dispo':'O'});">
        <input type="radio" name="options-%(date)s" id="options-%(date)s-O">Présent</label>
        <label class="btn %(P)s btn-danger " onclick="Dajaxice.cine.dispo(Dajax.process,{'date':'%(date)s','dispo':'P'});">
        <input type="radio" name="options-%(date)s" id="options-%(date)s-P">Absent</label>
        <label class="btn %(N)s btn-primary" onclick="Dajaxice.cine.dispo(Dajax.process,{'date':'%(date)s','dispo':'N'});">
        <input type="radio" name="options-%(date)s" id="options-%(date)s-N">Ne sais pas</label>
    </div>
    """ % {
            'date': soiree.date.strftime('%Y-%m-%d_%H-%M'),
            'O': 'active' if dtw.dispo == 'O' else '',
            'P': 'active' if dtw.dispo == 'P' else '',
            'N': 'active' if dtw.dispo == 'N' else '',
            }
