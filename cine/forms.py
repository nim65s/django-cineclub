from datetime import date

from django.forms import ModelForm, ValidationError

from .models import Soiree


class SoireeForm(ModelForm):
    def clean_date(self):
        if self.cleaned_data['date'] < date.today():
            raise ValidationError('On ne peut pas organiser de soirées dans le passé…')
        return self.cleaned_data['date']

    class Meta:
        model = Soiree
        fields = ['date', 'time']
