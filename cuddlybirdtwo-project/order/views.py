from django.shortcuts import render
from django.views import generic
from .models import Order, OrderItem
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
class SingleOrder(generic.DetailView):
    model = Order
    template_name = 'thanks.html'

class OrderList(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'order_list.html'

    def get_queryset(self):
        print(self.request.user)
        return Order.objects.filter(user=self.request.user)

class OrderDetail(LoginRequiredMixin, generic.DetailView):
    model = OrderItem
    template_name = 'order_detail.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = OrderItem.objects.filter(order=self.kwargs['pk'])
        return context
