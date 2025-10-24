from events.models import Event, Participant, Category
from django import forms
from django.contrib.auth.models import User
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm

class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()



    default_classes = 'border-2 border-gray-300 rounded-lg w-full p-3 shadow-sm focus:outline-none focus:border-rose-500 focus:ring-rose-500'
    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f'Enter your {field.label.lower()}'
                })
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f'Enter your event {field.label.lower()}'
                })

            elif isinstance(field.widget, forms.SelectDateWidget):
                field.widget.attrs.update({
                    'class': self.default_classes,
                })
            elif isinstance(field.widget, forms.TimeInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                }),
            elif isinstance(field.widget, forms.EmailInput):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder': f'Enter your {field.label.lower()}'
                }),
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    'class': self.default_classes,
                })
            elif isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': self.default_classes
                })
                


class EventModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'end_date', 'start_date', 'time', 'location', 'category']

        widgets = {
            'name': forms.TextInput(),
            'description': forms.Textarea(),
            'start_date': forms.SelectDateWidget(attrs={'type':'date'}),
            'end_date': forms.SelectDateWidget(attrs={'type': 'date'}),
            'time': forms.TimeInput(format='%H:%M', attrs={'type':'time'}),
            'location': forms.TextInput(),
            'category': forms.Select()
        }

        labels = {
            'name': 'Event Title',
            'description': 'Event Description',
            'start_date': 'Event Start Date',
            'end_date': 'Event End Date',
            'time': 'Event Start Time',
            'location': 'Event Location',
            'category': 'Event Category'
        }

class ParticipantModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'email']

        widgets = {
            'name': forms.TextInput(),
            'email': forms.EmailInput()
        }

        labels = {
            'name': 'Participant Name',
            'email': 'Participant Email'
        }

class CategoryModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

        widgets = {
            'name': forms.TextInput(),
            'description': forms.Textarea()
        }

        labels = {
            'name': 'Category',
            'description': 'Category Description'
        }


class RegisterForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name','password1', 'confirm_password']

    def clean_password(self):
        password1 = self.clean_data.get('password1')
        errors = []

        if len(password1 < 8):
            errors.append('Password must contain 8 characters')
        elif re.search(r'[A-Z]', password1):
            errors.append('Password must contain at least one capital letters')
        elif re.search(r'[a-z]', password1):
            errors.append('Password must contain at least one small letters')
        elif re.search(r'[0-9]', password1):
            errors.append('Password must contain at least one digit')
        elif re.search(r'[!@#$%&*]', password1):
            errors.append('Password must contain at least one special character')
        
        if errors:
            raise ValidationError(errors)    
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        confirm_password = cleaned_data.get('confirm_password')
        if password1 and confirm_password and password1 != confirm_password:
            raise ValidationError('Both passwords do not match')
        elif not password1:
            raise ValidationError('You did not fill in the password')
        elif not confirm_password:
            raise ValidationError('You did not confirm the password')
        return cleaned_data
    

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_exists = User.objects.filter(email=email).exists()
        if email_exists:
            raise ValidationError('A user with that email already exists')
        return email

    
class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    