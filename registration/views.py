from django.shortcuts import render, redirect
from .forms import RegistrationForm, UserregForm
from logging import exception
from multiprocessing import context
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages
import random
from .models import Userreg

from django.core.mail import EmailMessage
import threading

from django.urls import reverse

# required to build email activation
from django.core.mail import EmailMessage
from django.views import View
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_text,  force_bytes
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token


class FasterActivateEmail(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


def user_registration(request):
    accepted_domains = ['morgan.edu', 'imsu.edu', 'umd.edu']
    registration_form = RegistrationForm() 
    userreg_form = UserregForm()
    if request.method == "POST":
        registration_form = RegistrationForm(request.POST)
        userreg_form = UserregForm(request.POST)
        if registration_form.is_valid() and userreg_form.is_valid():
            username = registration_form.cleaned_data.get('username')
            email = registration_form.cleaned_data.get('email')
            user_domain = email.split('@')[1]
            if user_domain in accepted_domains:
                user = registration_form.save()
                userreg = userreg_form.save(commit=False)
                userreg.user = user
                userreg.domain = True
                userreg.save()
                messages.success(request, 'Account Successfully Created for' + username.upper() +
                                'and activation email sent to:' + email + ", \n" + "Please visit your email to activate your account...")
                #implementation for email activation before using the account
                current_user = User.objects.get(username=username)
                #forcebyte allows encoded URL to be sent over the internet
                uidb64 = urlsafe_base64_encode(force_bytes(current_user.pk))
                print('current is: ', current_user)
                token = account_activation_token.make_token(user=current_user)
                domain = get_current_site(request).domain
            
                link = reverse('activate_account', kwargs={
                    'uidb64': uidb64,
                    'token': token
                })
                activate_url = 'http://'+domain+link
                current_user.is_active = False
                current_user.save()
                email_subject = 'Activate Your Account'
                email_body = "Hi "+current_user.username + "Please use this link to activate your account \n" + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreplay@ogalandlordpro.org',
                    [email],
                )
                FasterActivateEmail(email).start()
                return redirect('user_login')
            else:
                messages.info(request, "The Domain you entered is not allowed...")

    registration_form = RegistrationForm() 
    userreg_form = UserregForm()
    context = {
        'registration_form': registration_form,
        'userreg_form': userreg_form
    }
    return render(request, 'registration/sign-up.html', context)


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if user.is_active:
                return redirect('user_login')
            else:
                user.is_active = True
                user.save()
            messages.success(request, "Account Successfully Activated")
        except Exception as ex:
            pass
            
        return redirect('user_login')

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Your account is not yet activated...")
    

    return render(request, 'registration/user_login.html')


def  user_logout(request):
    logout(request)
    return redirect('/')

