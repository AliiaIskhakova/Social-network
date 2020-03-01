# позволяет узнать ссылку на URL по его имени, параметр name функции path
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CreationForm
from django.shortcuts import render, redirect


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("posts:index")
    template_name = "signup.html"

def send_mail_signup(email):
    send_mail('Подтверждение регистрации Yatube', 'Вы зарегистрированы!',
              'Yatube.ru <admin@yatube.ru>',[email], fail_silently=False)