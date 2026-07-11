from django import forms
from django.core.validators import RegexValidator
from .models import Order

# Fix #16: Phone number validator
phone_validator = RegexValidator(
    regex=r'^\+?[\d\s\-\(\)]{7,20}$',
    message='Введіть коректний номер телефону (7–20 цифр, допускаються +, пробіли, дефіси, дужки).'
)

INPUT_CLASS = (
    'w-full bg-transparent border-0 border-b border-[#ccc] px-0 py-2 text-sm '
    'text-black placeholder-[#aaa] focus:outline-none focus:border-black transition-colors'
)

SELECT_CLASS = (
    'w-full bg-transparent border-0 border-b border-[#ccc] px-0 py-2 text-sm '
    'text-black focus:outline-none focus:border-black transition-colors appearance-none cursor-pointer'
)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'email', 'region', 'city', 'branch', 'comment']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Введіть ПІБ',
            }),
            'phone': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': '+380',
            }),
            'email': forms.EmailInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Email (необов\'язково)',
            }),
            'region': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Оберіть область',
                'id': 'id_region',
            }),
            'city': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Спочатку виберіть область',
                'id': 'id_city',
            }),
            'branch': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Спочатку виберіть місто',
                'id': 'id_branch',
            }),
            'comment': forms.Textarea(attrs={
                'class': INPUT_CLASS + ' resize-none',
                'placeholder': 'Коментар до замовлення',
                'rows': 3,
                'id': 'id_comment',
            }),
        }
        labels = {
            'full_name': 'ПІБ',
            'phone': 'Телефон',
            'email': 'Email',
            'region': 'Область',
            'city': 'Місто',
            'branch': 'Відділення',
            'comment': 'Коментар',
        }
