from django.shortcuts import render
from django.views import generic
from django.db.models import Q
from .models import Category, Product

# Create your views here.

class HomePage(generic.ListView):
    model = Product
    template_name = 'index.html'

class SingleProduct(generic.DeleteView):
    model = Product
