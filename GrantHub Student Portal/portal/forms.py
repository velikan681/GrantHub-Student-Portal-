from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Application, Category, Grant, User


FORM_CONTROL = {'class': 'form-control'}


class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'full_name', 'email', 'university', 'faculty', 'course',
            'education_level', 'interests', 'password1', 'password2',
        )
        widgets = {
            'full_name': forms.TextInput(attrs=FORM_CONTROL),
            'email': forms.EmailInput(attrs=FORM_CONTROL),
            'university': forms.TextInput(attrs=FORM_CONTROL),
            'faculty': forms.TextInput(attrs=FORM_CONTROL),
            'course': forms.NumberInput(attrs={**FORM_CONTROL, 'min': 1, 'max': 6}),
            'education_level': forms.TextInput(attrs=FORM_CONTROL),
            'interests': forms.TextInput(attrs={**FORM_CONTROL, 'placeholder': 'IT, медицина, экология'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs=FORM_CONTROL))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs=FORM_CONTROL))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'university', 'faculty', 'course', 'education_level', 'interests']
        widgets = {
            field: forms.TextInput(attrs=FORM_CONTROL)
            for field in ['full_name', 'university', 'faculty', 'education_level', 'interests']
        } | {
            'email': forms.EmailInput(attrs=FORM_CONTROL),
            'course': forms.NumberInput(attrs={**FORM_CONTROL, 'min': 1, 'max': 6}),
        }


class GrantForm(forms.ModelForm):
    class Meta:
        model = Grant
        fields = [
            'title', 'description', 'organization', 'country', 'category',
            'opportunity_type', 'education_level', 'requirements',
            'documents', 'deadline', 'official_link',
        ]
        widgets = {
            'title': forms.TextInput(attrs=FORM_CONTROL),
            'description': forms.Textarea(attrs={**FORM_CONTROL, 'rows': 4}),
            'organization': forms.TextInput(attrs=FORM_CONTROL),
            'country': forms.TextInput(attrs=FORM_CONTROL),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'opportunity_type': forms.Select(attrs={'class': 'form-select'}),
            'education_level': forms.TextInput(attrs=FORM_CONTROL),
            'requirements': forms.Textarea(attrs={**FORM_CONTROL, 'rows': 3}),
            'documents': forms.Textarea(attrs={**FORM_CONTROL, 'rows': 3}),
            'deadline': forms.DateInput(attrs={**FORM_CONTROL, 'type': 'date'}),
            'official_link': forms.URLInput(attrs=FORM_CONTROL),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cv_file', 'motivation_letter', 'certificate_file']
        widgets = {
            'cv_file': forms.FileInput(attrs=FORM_CONTROL),
            'motivation_letter': forms.FileInput(attrs=FORM_CONTROL),
            'certificate_file': forms.FileInput(attrs=FORM_CONTROL),
        }


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': 'form-select form-select-sm'})}


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs=FORM_CONTROL)}
