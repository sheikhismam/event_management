from events.models import Event, Category, RSVP, CustomUser
from django import forms
from django.contrib.auth.models import User, Group, Permission
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from events.models import CustomUser

User = get_user_model()

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
        fields = ['name', 'description', 'end_date', 'start_date', 'time', 'location', 'category', 'asset']  # 'participants,'

        widgets = {
            'name': forms.TextInput(),
            'description': forms.Textarea(),
            'start_date': forms.SelectDateWidget(attrs={'type':'date'}),
            'end_date': forms.SelectDateWidget(attrs={'type': 'date'}),
            'time': forms.TimeInput(format='%H:%M', attrs={'type':'time'}),
            'location': forms.TextInput(),
            'category': forms.Select(),
            'asset': forms.ClearableFileInput(),
            # 'participants': forms.CheckboxSelectMultiple()
        }

        labels = {
            'name': 'Event Title',
            'description': 'Event Description',
            'start_date': 'Event Start Date',
            'end_date': 'Event End Date',
            'time': 'Event Start Time',
            'location': 'Event Location',
            'asset': 'Upload Image',
            'category': 'Event Category',
            # 'participants': 'Select participants'
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

# class ParticipantModelForm(StyledFormMixin, forms.ModelForm):
#     password1 = forms.CharField(widget=forms.PasswordInput())
#     confirm_password = forms.CharField(widget=forms.PasswordInput())
#     event_name = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'event_name', 'password1', 'confirm_password']


class RegisterForm(StyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        errors = []

        if len(password1) < 8:
            errors.append('Password must contain at least 8 characters')
        if not re.search(r'[A-Z]', password1):
            errors.append('Password must contain at least one capital letter')
        if not re.search(r'[a-z]', password1):
            errors.append('Password must contain at least one small letter')
        if not re.search(r'[0-9]', password1):
            errors.append('Password must contain at least one digit')
        if not re.search(r'[!@#$%&*]', password1):
            errors.append('Password must contain at least one special character')

        if errors:
            raise ValidationError(errors)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        confirm_password = cleaned_data.get('confirm_password')

        if password1 and confirm_password and password1 != confirm_password:
            raise ValidationError('confirm_password','Both passwords do not match')
        if not password1:
            raise ValidationError('password1', 'You did not fill in the password')
        if not confirm_password:
            raise ValidationError('confirm_password' ,'You did not confirm the password')
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with that email already exists')
        return email

    
class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class AssignRoleForm(StyledFormMixin, forms.ModelForm):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label = 'Assign a role'
    )
    class Meta:
        model = User
        fields = []


class CreateGroupForm(StyledFormMixin, forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required=False,
        label='Assign permissions'
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

class RSVPForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['response']

"""
class EditProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    bio = forms.CharField(required=False, widget=forms.Textarea, label='bio')
    profile_image = forms.ImageField(required=False, label='profile_image')

    def __init__(self, *args, **kwargs):
        self.userprofile = kwargs.pop('userprofile', None)
        super().__init__(*args, **kwargs)
        
        if self.userprofile:
            self.fields['bio'].initial = self.userprofile.bio
            self.fields['profile_image'].initial = self.userprofile.profile_image

    def save(self, commit = True):
        user = super().save(commit=False)

        if self.userprofile:
            self.userprofile.bio = self.cleaned_data.get('bio')
            self.userprofile.profile_image = self.cleaned_data.get('profile_image')

            if commit:
                self.userprofile.save()
        if commit:
            user.save()
"""
class EditProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_image']

class CustomPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass

class CustomPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass

class CustomPasswordResetConfirmForm(StyledFormMixin, SetPasswordForm):
    pass