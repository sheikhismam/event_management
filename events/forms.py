from events.models import Event, Participant, Category
from django import forms


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

