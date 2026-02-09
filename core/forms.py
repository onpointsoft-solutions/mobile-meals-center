from django import forms
from superadmin.models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'subject', 'description', 'order_number']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief summary of your issue',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Please provide detailed information about your complaint...',
                'required': True
            }),
            'order_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Order number (if applicable)'
            })
        }
        labels = {
            'category': 'Issue Category',
            'subject': 'Subject',
            'description': 'Description',
            'order_number': 'Order Number (Optional)'
        }
