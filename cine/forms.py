from django.forms import ModelForm, ValidationError
from django.utils import timezone

from ndh.forms import AccessibleDateTimeField

from .models import Soiree


class SoireeForm(ModelForm):
    moment = AccessibleDateTimeField()

    def clean_moment(self):
        if self.cleaned_data["moment"] < timezone.now():
            raise ValidationError("On ne peut pas organiser de soirées dans le passé…")
        return self.cleaned_data["moment"]

    class Meta:
        model = Soiree
        fields = ["moment"]
