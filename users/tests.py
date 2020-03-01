from django.test import TestCase, Client
from django.core import mail
from django.contrib.auth import get_user_model
from posts.models import Post
from django.urls import reverse

User = get_user_model()


class EmailTest(TestCase):
    """проверка письма с подтверждением регистрации"""
    def setUp(self):
        self.client = Client() # создание тестового клиента
        self.user = User.objects.create_user(
                    username="sarah", email="connor.s@skynet.com", password="12345")

    def test_send_email(self):
        mail.send_mail('Тема письма', 'Текст письма.',
                       'admin@yatube.ru', ['connor.s@skynet.com'], fail_silently=False,) # выводить описание ошибок

        self.assertEqual(len(mail.outbox), 1) # Проверяем, что письмо лежит в исходящих

        self.assertEqual(mail.outbox[0].subject, 'Тема письма') # Проверяем, что тема первого письма правильная.


class ProfileTest(TestCase):
    """проверка создания персональной страницы после регистрации пользователя"""
    def setUp(self):
        self.client = Client() 
        self.user = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")
                
    def test_profile(self):
        response = self.client.get("/sarah/") # формируем GET-запрос к странице профиля
        self.assertEqual(response.status_code, 200) # проверяем что страница найдена


class ErrorTest(TestCase):
    """проверка страниц ошибок"""
    def setUp(self):
        self.client = Client()
        
    def test_page404(self):
        """проверка на возвращение сервером ошибки 404"""
        response = self.client.get("/test404/")
        self.assertEqual(response.status_code, 404)

class FollowTest(TestCase):
    """проверка на возможность авторизованному пользователю подписываться"""
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")
        self.user2 = User.objects.create_user(
                username="arny", email="arny.s@skynet.com", password="12345")

        self.client.force_login(self.user1)

    def test_follow(self):
        #подписка
        response = self.client.get("/arny/follow/")
        #количество объектов где sarah является подписчиком arny
        follow = Follow.objects.get(user='sarah',author='arny').count()
        self.assertEqual(follow, 1)

        #отписка
        response = self.client.get("/arny/unfollow/")
        follow = Follow.objects.get(user='sarah',author='arny').count()
        self.assertEqual(follow, 0)