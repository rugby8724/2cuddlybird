from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import get_template

from .models import Cart, CartItem
from store.models import Product
from order.models import Order, OrderItem

import stripe

from django.contrib.auth import get_user_model
User = get_user_model()
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
            )
        cart.save()
    try:
        #won't add product if there is not enough stock
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1

        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
                    product = product,
                    quantity = 1,
                    cart = cart
                    )
        cart_item.save()

    return redirect('cart:cart_detail')

def cart_detail(reqest, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total * 100)
    description = "CuddlyBird"
    data_key = settings.STRIPE_PUBLISHABLE_KEY

    if request.method =='POST':
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            billingName = request.POST['stripeBillingName']
            billingAddress1 = request.POST['stripeBillingAddressLine1']
            billingCity = request.POST['stripeBillingAddressCity']
            billingPostcode = request.POST['stripeBillingAddressZip']
            billingCountry = request.POST['stripeBillingAddressCountryCode']
            shippingName = request.POST['stripeShippingName']
            shippingAddress1 = request.POST['stripeShippingAddressLine1']
            shippingCity = request.POST['stripeShippingAddressCity']
            shippingPostcode = request.POST['stripeShippingAddressZip']
            shippingCountry = request.POST['stripeShippingAddressCountryCode']
            customer = stripe.Customer.create(
                        email = email,
                        source = token
                        )
            charge = stripe.Charge.create(
                        amount = stripe_total,
                        currency = 'usd',
                        description = description,
                        customer = customer.id
                        )
            if request.user.is_anonymous:
                use = None
            else:
                user = request.user

            try:
                order_details = Order.objects.create(
                                token = token,
                                user = user,
                                total = total,
                                emailAddress = email,
                                billingName = billingName,
                                billingAddress1 = billingAddress1,
                                billingCity = billingCity,
                                billingPostcode = billingPostcode,
                                billingCountry = billingCountry,
                                shippingName = shippingName,
                                shippingAddress1 = shippingAddress1,
                                shippingCity = shippingCity,
                                shippingPostcode = shippingPostcode,
                                shippingCountry = shippingCountry
                                )
                order_details.save()
                for order_item in cart_items:
                    or_item = OrderItem.objects.create(
                            product = order_item.product.name,
                            quantity = order_item.quantity,
                            price = order_item.product.price,
                            order = order_details
                            )
                    or_item.save()

                    #reduce stock
                    products = Product.objects.get(id=order_item.product.id)
                    products.stock = int(order_item.product.stock - order_item.quantity)
                    products.save()
                    order_item.delete()

                    #print message when order is completed
                    print('the order has been created')
                try:
                    # calling the send email function
                    sendEmail(order_details.id)
                    print('The order email has been sent to the customer')
                except IOError as e:
                    return e

                return redirect('order:thanks', pk=order_details.id)
            except ObjectDoesNotExist:
                pass
        except stripe.error.CardError as e:
            return False, e

    return render(request, 'cart.html', dict(cart_items = cart_items, total = total, counter = counter, data_key = data_key, stripe_total = stripe_total, description = description ))

def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart_detail')

def cart_remove_product(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart_detail')

def sendEmail(order_id):
    transaction = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=transaction)
    try:
        #Sending the order to the customer
        mail_sub = f"Cuddly Bird - New Order #{transaction.id}"
        to_email = [f'{transaction.emailAddress}', settings.DEFAULT_FROM_EMAIL]
        from_email = settings.DEFAULT_FROM_EMAIL
        order_information = {
        'transaction': transaction,
        'order_items': order_items
        }
        order_message = get_template('email/email.html').render(order_information)
        msg = EmailMessage(mail_sub, order_message, to=to_email, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
        # send_mail(mail_sub, order_message, from_email, to_email, fail_silently=True)
    except IOError as e:
        return e
