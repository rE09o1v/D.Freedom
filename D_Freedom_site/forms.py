from django import forms
from .models import Estimate, EstimateItem

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='お名前',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='メールアドレス',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        max_length=200,
        label='件名',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label='メッセージ',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=True
    )

class EstimateItemForm(forms.ModelForm):
    class Meta:
        model = EstimateItem
        fields = ['name', 'description', 'quantity', 'unit_price', 'tax_rate']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = ['client_name', 'client_address', 'client_email', 'client_tel', 'notes']
        widgets = {
            'client_address': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        } 