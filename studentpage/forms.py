from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Candidate, Transcript


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email Address',
                             widget=forms.EmailInput(attrs={'placeholder': 'Email...', 'class': 'form-control'}))
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput(
                                    attrs={'placeholder': 'Enter password...', 'class': 'form-control'}))
    password2 = forms.CharField(label='Repeat Password',
                                widget=forms.PasswordInput(
                                    attrs={'placeholder': 'Re-enter password...', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register Account'))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def save(self, commit=True):
        user = super(CreateUserForm, self).save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


ALLOWED_FILE_TYPES = ['pdf', 'jpg', 'jpeg', 'png']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            'Birth_certificate',
            'identification_card_file',
            'photo',
            'passport',
            'certificate_of_good_conduct',
            'High_School_file',
            'University_file',
            'Nursing_Certificate',
            'Licence_file',
            'Institution_file',
            'resume_file',

        ]
        labels = {
            'photo': 'Passport Photo',
            'High_School_file': 'Secondary school results slip',
            'identification_card_file': 'National ID',
            'Licence_file': 'Nursing Council Practicing Licence',
            'Nursing_Certificate': 'Nursing Council Certificate',
            'resume_file': 'Resume or CV',
            'University_file': 'University Transcript',
            'Institution_file': 'Work Experience',
            'passport': 'Passport'
        }
        help_texts = {
            'photo': 'Upload a clear passport photo. Upload a new file to replace the current file',
            'passport': 'Upload a clear passport document. Upload a new file to replace the current file',
            'identification_card_file': 'Scan of your national ID. Upload a new file to replace the current file',
            'certificate_of_good_conduct': 'Upload a clear Certificate. Upload a new file to replace the current file',
            'High_School_file': 'Upload a clear Secondary school results slip. Upload a new file to replace the current file',
            'University_file': 'Upload a clear Certificate. Upload a new file to replace the current file',
            'Nursing_Certificate': 'Upload a clear Certificate. Upload a new file to replace the current file',
            'Licence_file': 'Upload a clear Certificate. Upload a new file to replace the current file',
            'Institution_file': 'Upload a clear Certificate. Upload a new file to replace the current file',
            'resume_file': 'Upload a clear Certificate. Upload a new file to replace the current file',
            'Birth_certificate': 'Upload a clear Certificate. Upload a new file to replace the current file',
            # Add more help texts for other fields as necessary
        }

    def __init__(self, *args, **kwargs):
        super(DocumentUploadForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)

        if instance:
            for field_name in self.fields:
                file_field = getattr(instance, field_name)
                if file_field:
                    # Assume a method `file_url` exists on the model to get the file's URL
                    # This is hypothetical and would need to be implemented on your model
                    file_url = getattr(file_field, 'url', None)
                    if file_url:
                        # Store the URL in the field's widget attrs for access in the template
                        self.fields[field_name].widget.attrs['data-file-url'] = file_url
                    else:
                        # If no URL, just indicate a file is present
                        self.fields[field_name].widget.attrs['data-file-present'] = 'true'

    def clean(self):
        cleaned_data = super().clean()
        for field_name, field in self.fields.items():
            if field_name in self.Meta.fields and not field.disabled:
                file = cleaned_data.get(field_name)
                if file:
                    if not file.name.split('.')[-1].lower() in ALLOWED_FILE_TYPES:
                        self.add_error(field_name, "Only PDF, JPG, JPEG and PNG files are allowed.")
                    if file.size > MAX_FILE_SIZE:
                        self.add_error(field_name, "File too large ( > 10MB ).")
        return cleaned_data


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render


@require_http_methods(["GET", "POST"])
def resume_builder(request):
    if request.method == 'POST':
        # Handle form submission (we'll implement this later)
        pass
    else:
        # Render the empty form
        return render(request, 'resume_builder.html')


from django import forms
from .models import Resume


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        exclude = ['candidate', 'version', 'is_current', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if isinstance(self.fields[field], forms.CharField) and not isinstance(self.fields[field].widget,
                                                                                  forms.Textarea):
                self.fields[field].widget = forms.Textarea(attrs={'rows': 3})
