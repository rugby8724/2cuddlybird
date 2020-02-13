from django import forms

class ContactForm(forms.Form):
    form_email = forms.EmailField(label='Your Email', max_length=257, required=True)
    subject = forms.CharField(max_length=257, required=True)
    message = forms.CharField(widget=forms.Textarea)
