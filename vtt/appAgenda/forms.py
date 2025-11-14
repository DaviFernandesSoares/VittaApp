from django import forms
from django.utils import timezone
from .models import RecurringSlot, AvailabilitySlot

class RecurringSlotForm(forms.ModelForm):
    class Meta:
        model = RecurringSlot
        fields = ['title','weekday','start_time','end_time','start_date','end_date','capacity','active']

    def clean(self):
        cleaned = super().clean()
        st = cleaned.get('start_time')
        ed = cleaned.get('end_time')
        if st and ed and ed <= st:
            raise forms.ValidationError('Hora de término deve ser posterior ao início.')
        return cleaned

class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['start','end','capacity']