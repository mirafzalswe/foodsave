from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div
from crispy_forms.bootstrap import FormActions
from .models import Order

User = get_user_model()


class CheckoutForm(forms.ModelForm):
    """Form for checkout process"""
    
    class Meta:
        model = Order
        fields = ['delivery_type', 'delivery_address', 'payment_method', 'notes']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('delivery_type', css_class='form-group col-md-6 mb-3'),
                Column('payment_method', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'delivery_address',
            'notes',
            FormActions(
                Submit('submit', 'Подтвердить заказ', css_class='btn btn-primary btn-lg w-100'),
                css_class='mt-3'
            )
        )
        
        # Add custom styling
        self.fields['delivery_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['payment_method'].widget.attrs.update({'class': 'form-select'})
        self.fields['delivery_address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите адрес доставки...'
        })
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Дополнительные пожелания или инструкции...'
        })
    
    def clean_delivery_address(self):
        delivery_type = self.cleaned_data.get('delivery_type')
        delivery_address = self.cleaned_data.get('delivery_address')
        
        if delivery_type == 'delivery' and not delivery_address:
            raise forms.ValidationError('Адрес доставки обязателен для доставки.')
        
        return delivery_address


class OrderSearchForm(forms.Form):
    """Form for searching orders"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по номеру заказа...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Все статусы')] + Order.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row g-3'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='col-md-4'),
                Column('status', css_class='col-md-2'),
                Column('date_from', css_class='col-md-2'),
                Column('date_to', css_class='col-md-2'),
                Column(
                    Submit('submit', 'Поиск', css_class='btn btn-primary'),
                    css_class='col-md-2 d-flex align-items-end'
                ),
            )
        )
