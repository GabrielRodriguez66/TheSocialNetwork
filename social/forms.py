from django import forms

class ShoutForm(forms.Form):
    shout_text = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'cols':50}), label='Shout', max_length=100, required=True)