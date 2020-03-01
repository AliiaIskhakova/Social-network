from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

class Post(models.Model):
    text = models.TextField(max_length=600)
    pub_date = models.DateTimeField("date published", auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True,
    null=True, related_name="group") 
    image = models.ImageField(upload_to='posts/media/', blank=True,
    null=True)  # поле для картинки

    def __str__ (self):
        #выводим текст поста
        return self.text

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment_post")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_author")
    text = models.TextField(max_length=200)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)


class Follow(models.Model):
    #пользователь, который подписывается
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    #пользователь, на которого подписываются
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    

    

