from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.emailView, name='contact_page'),
    path('thankyou/', views.ThankYou.as_view(), name='thankyou'),
]
