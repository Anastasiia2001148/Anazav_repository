
from django import forms
from .models import Author, Quote

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['fullname', 'born_date', 'born_location', 'description']  # Укажите поля, которые хотите включить в форму


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['quote', 'author', 'tags']  # Укажите поля, которые хотите включить в форму
