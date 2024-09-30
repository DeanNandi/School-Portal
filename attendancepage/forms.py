from django import forms
from .models import ClassAttendance, ABSENT_REASON_CHOICES


class ClassAttendanceForm(forms.ModelForm):
    present = forms.BooleanField(required=False)

    class Meta:
        model = ClassAttendance
        fields = ['present', 'absent_reason']
        widgets = {
            'absent_reason': forms.Select(choices=[('', '---------')] + list(ABSENT_REASON_CHOICES))
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['absent_reason'].required = False

    def clean(self):
        cleaned_data = super().clean()
        present = cleaned_data.get('present', False)
        absent_reason = cleaned_data.get('absent_reason')

        if not present and not absent_reason:
            raise forms.ValidationError(
                {'absent_reason': "Please provide an absent reason when marking a student as not present."})

        if present:
            cleaned_data['absent_reason'] = ''

        return cleaned_data