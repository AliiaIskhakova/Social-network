from django.test import TestCase, Client, override_settings
from django.core import mail
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Follow
from django.urls import reverse

User = get_user_model()

TEST_CACHE = {
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

class UnloginTest(TestCase):
    """проверка на редирект со страницы создания поста неавторизованного пользователя"""
    def setUp(self):
        self.client = Client()

    def test_not_login(self):
        # POST запрос на страницу создания поста
        response = self.client.post(reverse('posts:new_post'), follow=True)
        # редирект на страницу входа, а затем на страницу создания поста
        # так работает декоратор @login_required
        self.assertRedirects(response, '/auth/login/?next=/new/')
    

class PostNewTest(TestCase):
    def setUp(self):
        self.client = Client() 
        self.user = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")
        self.client.force_login(self.user)
        self.post = Post.objects.create(text="My post!", author=self.user)

    def test_new(self):
        """проверка на возможность опубликовать новый пост авторизованному пользователю"""
        response = self.client.get("/sarah/")
        # проверяем, что при отрисовке страницы был получен список из 1 записи
        # новый пост опубликован на странице профиля
        self.assertEqual(len(response.context['post']), 1)


    @override_settings(CACHES=TEST_CACHE)
    def test_new_post(self):
        """проверка на отображение нового поста на всех связанных с ним страницах"""
        urls = ('' , '/sarah/', '/sarah/1/')
        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, text="My post!")


    def test_edit(self):
        """проверка на возможность авторизованному пользователю редактировать свой пост
           отредактированный пост отображается на всех связанных с ним страницах"""
        # GET запрос на страницу редактирования поста
        response = self.client.get("/sarah/1/edit")
        self.assertEqual(response.status_code, 301)

        # редактируем пост 
        self.post.text ="Edited"
        self.post.save()

        urls = ('' , '/sarah/', '/sarah/1/')
        for url in urls:
            response = self.client.get(url)
            self.assertContains(response, text="Edited")


class ImageTest(TestCase):
    """проверка корректности отображения изображений"""
    def setUp(self):
        self.client = Client() 
        self.user = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")
        self.client.force_login(self.user)

        self.group = Group.objects.create(title='super', slug='super', description='description')
        with open('media/posts/media/no-photo.jpg', 'rb') as fp: 
            self.client.post('/new/', {'group': 1, 'text': 'Text', 'image': fp}) 

    def test_image(self):
        urls = ('' , '/sarah/', '/sarah/1/', '/group/super/')
        for url in urls:
            self.assertContains(response, '<img', status_code=200)


class ImageTest(TestCase):
    """проверка ситуации при загрузке не графического файла"""
    def setUp(self):
        self.client = Client() 
        self.user = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")
        self.client.force_login(self.user)

        self.group = Group.objects.create(title='super', slug='super', description='description')
        with open('media/posts/media/1.docx', 'rb') as fp: 
            self.response = self.client.post('/new/', {'group': 1, 'text': 'Text', 'image': fp}, follow=True) 

    def test_image(self):
        # проверка на валидность формы загрузки изображения
        self.assertFormError(self.response, 'form', 'image', 'Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением.')


class PostFollowTest(TestCase):
    """проверка на появление поста в ленте у подписчиков"""
    def setUp(self):
        self.client = Client() 

        # создаю двух пользователей и логиню 1го
        self.user1 = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")
        self.user2 = User.objects.create_user(
                username="arny", email="arny.s@skynet.com", password="12345") 
        self.client.force_login(self.user1)

        # подписываю его на 2го
        Follow.objects.create(user=self.user1, author=self.user2)

        self.post = Post.objects.create(text="My post!", author=self.user2)

    def test_follow_post(self):
        response = self.client.get("/follow/") 
        self.assertContains(response, 'My post!', status_code=200)


class PostFollowTest(TestCase):
    """проверка на отсутствие поста в ленте у тех, кто не подписан"""
    def setUp(self):
        self.client = Client() 

        self.user1 = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")
        self.user2 = User.objects.create_user(
                username="arny", email="arny.s@skynet.com", password="12345") 
        self.client.force_login(self.user1)

        self.post = Post.objects.create(text="My post!", author=self.user2)

    def test_follow_post(self):
        response = self.client.get("/follow/")
        self.assertNotContains(response, 'My post!', status_code=200)
    

class CommentTest(TestCase):
    """проверка на возможность комментировать авторизованному пользователю"""
    def setUp(self):
        self.client = Client() 
        self.user = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")
        self.client.force_login(self.user)

        self.post = Post.objects.create(text="My post!", author=self.user)

    def test_comment(self):
        response = self.client.get("/sarah/1/comment/")
        self.assertEqual(response.status_code, 200)


class NotCommentTest(TestCase):
    """проверка на отсутствие возможности комментировать неавторизованному пользователю"""
    def setUp(self):
        self.client = Client() 
        self.user = User.objects.create_user(
                username="sarah", email="connor.s@skynet.com", password="12345")

        self.post = Post.objects.create(text="My post!", author=self.user)

    def test_not_comment(self):
        response = self.client.post(reverse('posts:add_comment', args=('sarah',1)), follow=True)
        # редирект на страницу входа, а затем на страницу создания комментария
        # так работает декоратор @login_required
        self.assertRedirects(response, '/auth/login/?next=/sarah/1/comment/')