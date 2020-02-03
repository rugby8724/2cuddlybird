from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from .forms import ContactForm
# Create your views here.
def emailView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            form_email = form.cleaned_data['form_email']
            message = form.cleaned_data['message']

            # Email Test
            mail_sub = 'Cuddly Bird Message: ' + subject +"."
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = ['jeremiah.d.wise@gmail.com','laluu.hu@gmail.com', 'cuddlybirdusa@gmail.com']


            contact_message = f'{subject},\n {message}\n\n from {form_email}'

            try:
                send_mail(mail_sub, contact_message, from_email, to_email)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('contact:thankyou')
    return render(request, "contact.html", {'form': form})

class ThankYou(TemplateView):
    template_name = 'thankyou.html'
