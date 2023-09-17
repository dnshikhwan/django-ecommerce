from django.shortcuts import render

from .models import ShippingAddress, Order, OrderItem

# import data from shopping cart
from cart.cart import Cart

# import jsonresponse
from django.http import JsonResponse

# for email
from django.core.mail import send_mail
from django.conf import settings


def checkout(request):

    # Users with account (prefilled the form)
    if request.user.is_authenticated:
        try:
            # authenticated users with shipping information
            shipping_address = ShippingAddress.objects.get(
                user=request.user.id)

            context = {'shipping': shipping_address}

            return render(request, 'payment/checkout.html', context=context)

        except:
            # authenticated users with no shipping information
            return render(request, 'payment/checkout.html')

    else:
        # guest user
        return render(request, 'payment/checkout.html')


def payment_success(request):

    # clear the shopping cart
    for key in list(request.session.keys()):
        # we name session_key in cart.py
        if key == 'session_key':
            del request.session[key]

    return render(request, 'payment/payment-success.html')


def payment_failed(request):
    return render(request, 'payment/payment-failed.html')

# complete order view


def complete_order(request):

    if request.POST.get('action') == 'post':

        # in get('name'), name is from ajax
        name = request.POST.get('name')
        email = request.POST.get('email')

        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')

        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')

        # combine all the shipping details
        shipping_address = (address1 + '\n' + address2 +
                            '\n' + city + '\n' + state + '\n' + zipcode)

        # get information from cart
        cart = Cart(request)

        # get the total price of items
        total_cost = cart.get_total()

        '''
            Order variations
            1) Create order -> Account users with/without shipping information
            2) Create order -> Guest users without an account

        '''

        # for authenticated user
        if request.user.is_authenticated:
            order = Order.objects.create(
                full_name=name, email=email, shipping_address=shipping_address, amount_paid=total_cost, user=request.user)

            # create instance for order model, take the order id that we just created above
            order_id = order.pk

            # loop over the product in cart, and create a order item list model
            product_list = []
            for item in cart:

                OrderItem.objects.create(
                    order_id=order_id, product=item['product'], quantity=item['qty'], price=item['price'], user=request.user)
                product_list.append(item['product'])

                all_products = product_list

                # send email after make a purchase
            send_mail('Order received', 'Hi!' + '\n\n' + 'Thank you for purchasing our product' +
                      '\n\n' + 'Please see your order below:' + '\n\n' + str(all_products) + '\n\n' + 'Total paid : $' + str(cart.get_total()), settings.EMAIL_HOST_USER, [email], fail_silently=False)

        # guest user
        else:
            order = Order.objects.create(
                full_name=name, email=email, shipping_address=shipping_address, amount_paid=total_cost)

            # create instance for order model, take the order id that we just created above
            order_id = order.pk

            # loop over the product in cart, and create a order item list model
            product_list = []
            for item in cart:

                OrderItem.objects.create(
                    order_id=order_id, product=item['product'], quantity=item['qty'], price=item['price'])
                product_list.append(item['product'])

            all_products = product_list

            # send email after make a purchase
            send_mail('Order received', 'Hi!' + '\n\n' + 'Thank you for purchasing our product' +
                      '\n\n' + 'Please see your order below:' + '\n\n' + str(all_products) + '\n\n' + 'Total paid : $' + str(cart.get_total()), settings.EMAIL_HOST_USER, [email], fail_silently=False)

        # return response
        order_success = True

        response = JsonResponse({'success': order_success})

        return response
