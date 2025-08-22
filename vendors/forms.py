from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div
from crispy_forms.bootstrap import FormActions
from .models import Vendor, Branch

User = get_user_model()


class VendorForm(forms.ModelForm):
    """Form for creating vendors (admin only)"""
    
    class Meta:
        model = Vendor
        fields = ['owner', 'type', 'name', 'description', 'logo', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('owner', css_class='form-group col-md-6 mb-3'),
                Column('type', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'name',
            'description',
            'logo',
            'is_active',
            FormActions(
                Submit('submit', 'Создать vendor', css_class='btn btn-primary btn-lg'),
                css_class='mt-3'
            )
        )
        
        # Add custom styling
        self.fields['owner'].widget.attrs.update({'class': 'form-select'})
        self.fields['type'].widget.attrs.update({'class': 'form-select'})
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Название заведения...'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Описание заведения...'
        })
        self.fields['logo'].widget.attrs.update({'class': 'form-control'})
        
        # Set queryset for owner field to show all users
        self.fields['owner'].queryset = User.objects.all()
        self.fields['owner'].empty_label = "Выберите владельца"


class BranchForm(forms.ModelForm):
    """Form for creating branches"""
    
    class Meta:
        model = Branch
        fields = ['vendor', 'name', 'address', 'latitude', 'longitude', 'phone', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'vendor',
            'name',
            'address',
            Row(
                Column('latitude', css_class='form-group col-md-6 mb-3'),
                Column('longitude', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'phone',
            'is_active',
            FormActions(
                Submit('submit', 'Создать филиал', css_class='btn btn-primary btn-lg'),
                css_class='mt-3'
            )
        )
        
        # Add custom styling
        self.fields['vendor'].widget.attrs.update({'class': 'form-select'})
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Название филиала...'
        })
        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Адрес филиала...'
        })
        self.fields['latitude'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Широта',
            'step': 'any'
        })
        self.fields['longitude'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Долгота',
            'step': 'any'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+7 (xxx) xxx-xx-xx'
        })
