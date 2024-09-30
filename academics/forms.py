from django import forms
from .models import Examination, StudentExam
from teacherpage.models import Cohort


class DateInput(forms.DateInput):
    input_type = 'date'


class StudentExamForm(forms.ModelForm):
    class Meta:
        model = StudentExam
        fields = ['name_of_exam', 'student', 'percentage_score', 'missed_exam_reason']


class ExaminationForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = ['examination_name', 'class_information', 'class_level', 'date_added']
        labels = {
            'class_information': 'Select Class',
            'class_level': 'Select Exam Type',

        }
        widgets = {
            'class_level': forms.Select(attrs={'id': 'class_level'}),
            'examination_name': forms.TextInput(attrs={'id': 'examination_name'}),
            'date_added': DateInput(),

        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user from kwargs
        super(ExaminationForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['class_information'].queryset = Cohort.objects.filter(teacher__user=user)
