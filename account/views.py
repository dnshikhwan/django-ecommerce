from django.shortcuts import redirect, render

from django.http import HttpResponse

# import from forms.py
from .forms import CreateUserForm

# package to collect our domain name
from django.contrib.sites.shortcuts import get_current_site
# import our token function
from .token import user_tokenizer_generate

# package to utilize our token
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from django.contrib.auth.models import User

# for login
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm

# to prevent unauthenticated user from accessing page
from django.contrib.auth.decorators import login_required

# to update user
from .forms import UpdateUserForm

# for messages
from django.contrib import messages

# for shipping address
# import form from payment app
from payment.forms import ShippingForm
# to make query
from payment.models import ShippingAddress

# for order items
from payment.models import Order, OrderItem

from django.db.models import Sum, Count


# register view remodelled
def register(request):

    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        # check is form valid
        if form.is_valid():

            # form.save()

            # set the user status to false and then register the user
            user = form.save()
            user.is_active = False
            user.save()

            # email verification setup
            current_site = get_current_site(request)

            subject = 'Account verification email'
            # render template to string
            message = render_to_string(
                'account/registration/email-verification.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': user_tokenizer_generate.make_token(user),
                })

            # send the email
            user.email_user(subject=subject, message=message)

            return redirect('email-verification-sent')

    context = {'form': form}

    return render(request, 'account/registration/register.html', context=context)


def email_verification(request, uidb64, token):
    # uniqueid
    unique_id = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=unique_id)

    # success
    if user and user_tokenizer_generate.check_token(user, token):
        user.is_active = True
        user.save()

        return redirect('email-verification-success')
    # failed
    else:
        return redirect('email-verification-failed')


def email_verification_sent(request):
    return render(request, 'account/registration/email-verification-sent.html')


def email_verification_success(request):
    return render(request, 'account/registration/email-verification-success.html')


def email_verification_failed(request):
    return render(request, 'account/registration/email-verification-failed.html')

# Login view


def my_login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            # check the username and password field match any user in the db
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)

                return redirect('dashboard')

    context = {'form': form}

    return render(request, 'account/my-login.html', context=context)

# Logout


def user_logout(request):
    # standard logout, when we logout, the session cleared and our shopping cart is empty once we logged out
    # auth.logout(request)

    try:
        for key in list(request.session.keys()):
            # dont delete our cart session named session_key
            if key == 'session_key':
                continue
            else:
                del request.session[key]
    except KeyError:
        pass

    # just put where we want the messages to be invoke
    messages.success(request, 'Logout success!')

    # wherever we want to redirect, that is where we want the message to be invoke
    return redirect('store')

# Dashboard


@login_required(login_url='my-login')
def dashboard(request):
    return render(request, 'account/dashboard.html')

# Profile management


@login_required(login_url='my-login')
def profile_management(request):

    # get the data of the current user and prepopulate in the form
    user_form = UpdateUserForm(instance=request.user)

    # updating our user's username and email
    if request.method == 'POST':
        # instance is get the data from the request based on current user
        user_form = UpdateUserForm(request.POST, instance=request.user)

        if user_form.is_valid():
            user_form.save()

            messages.info(request, 'Account updated')

            return redirect('dashboard')

    context = {'user_form': user_form}

    return render(request, 'account/profile-management.html', context=context)


@login_required(login_url='my-login')
def delete_account(request):

    # get the id of the authenticated user
    user = User.objects.get(id=request.user.id)

    if request.method == 'POST':
        user.delete()

        messages.error(request, 'Account deleted')

        return redirect('store')

    return render(request, 'account/delete-account.html')

# Shipping address view


@login_required(login_url='my-login')
def manage_shipping(request):
    try:
        # Account user with shipping information
        shipping = ShippingAddress.objects.get(user=request.user.id)

    except ShippingAddress.DoesNotExist:
        # Account user with no shipping information
        shipping = None

    # get the shipping result from try and except as an instance
    form = ShippingForm(instance=shipping)

    if request.method == 'POST':
        # if the user has shipping info, update it
        form = ShippingForm(request.POST, instance=shipping)

        if form.is_valid():
            # asign the user FK on the object
            shipping_user = form.save(commit=False)  # dont save the  form yet

            # adding the FK itself
            shipping_user.user = request.user

            # Save the form
            shipping_user.save()

            return redirect('dashboard')

    context = {'form': form}

    return render(request, 'account/manage-shipping.html', context=context)

# track view


@login_required(login_url='my-login')
def track_orders(request):
    try:
        orders = OrderItem.objects.filter(user=request.user)
        context = {'orders': orders}
        return render(request, 'account/track-orders.html', context=context)

    except:
        return render(request, 'account/track-orders.html')


# try to make admin panel
def admin_panel(request):
    sales = Order.objects.all().aggregate(Sum('amount_paid'))
    user = User.objects.all().aggregate(Count('username'))

    for key, value in user.items():
        user = value - 1

    for key, value in sales.items():
        total_sales = value

    context = {'total_sales': total_sales, 'user': user}
    return render(request, 'account/admin-panel.html', context=context)
