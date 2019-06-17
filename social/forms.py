from django import forms


class SearchForm(forms.Form):
    username = forms.CharField(label='Search', max_length=20, required=False)
