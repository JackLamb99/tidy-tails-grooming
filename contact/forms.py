from django import forms
from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = [
            "email",
            "phone",
            "first_name",
            "last_name",
            "subject",
            "message"
        ]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional",
                }
            ),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5
                }
            ),
        }
