
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from posts.models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required

User = get_user_model()


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    follow = False

    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user).exists()
        follow = True if following else False
        
    paginator = Paginator(post_list, 10) #  показывать по 10 записей на странице.
    page_number = request.GET.get('page') #  переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) #  получить записи с нужным смещением

    return render(request, 'index.html', {'page': page, 'paginator': paginator, 'follow':follow})


def group_posts(request, slug):
    """view-функция для страницы сообщества"""
    group = get_object_or_404(Group, slug=slug) 
    posts = Post.objects.filter(group=group).order_by("-pub_date").all()

    paginator = Paginator(posts, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)

    return render(request, "group.html", {"group": group, "posts": posts, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)

        if form.is_valid():
            #  сохраняем форму, но не отправляем в БД
            new_post = form.save(commit=False)
            #  получаем автора нового поста
            new_post.author = request.user
            new_post.save()
            return redirect('posts:index')
        return render(request, 'new.html', {'form': form, 'title':"Добавить запись", 'button':"Добавить"})

    return render(request, 'new.html', {'form': form, 'title':"Добавить запись", 'button':"Добавить"})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).order_by("-pub_date").all()
    following = False

    if request.user.is_authenticated:
        follow = Follow.objects.filter(user=request.user, author=author).exists()
        following = True if follow else False
    
    paginator = Paginator(posts, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)
    page_count = posts.count()
    
    return render(request, "profile.html", {'posts':posts, 'page_count':page_count, 'page': page, 'paginator': paginator, 
        'author':author, 'following':following})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = get_object_or_404(User, username=username)

    form = CommentForm()
    comments = Comment.objects.filter(post=post).all()
    comment_count = comments.count()

    page_count = Post.objects.filter(author=author).count()
    
    return render(request, "post.html", {'post':post, 'page_count':page_count, 'post_id':post_id, 'author':author, 
        'form':form, 'comments':comments, 'comment_count':comment_count})


def post_edit(request, username, post_id):
    #  текущий пользователь — это автор записи.
    post = get_object_or_404(Post, pk=post_id)
     
    if request.user != post.author:
        return redirect('posts:post', username=post.author, post_id=post_id)

    form = PostForm(instance=post)
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

        if form.is_valid(): 
            post = form.save() #  сохраняем форму и в БД
            return redirect('posts:post', username=post.author, post_id=post_id)
        return render(request, 'new.html', {'form': form, 'post':post})
            
    return render(request, "new.html", {'form': form, 'post':post, 'title':"Редактировать запись", 'button':"Сохранить"})


def page_not_found(request, exception):
    #  переменная exception содержит отладочную информацию, 
    #  выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(instance=post)
    comments = Comment.objects.filter(post=post).all()

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('posts:post', username=post.author, post_id=post_id)
        return render (request, 'post.html', {'form': form, 'post':post, 'comments':comments})
        
    return render(request, "post.html", {'form': form, 'post':post, 'comments':comments})


@login_required
def follow_index(request):
    """страница просмотра подписок"""
    follow = get_object_or_404(User, username=request.user.username) #кто подписывается
    #  получаю посты авторов, на которых подписан user 
    post_list = Post.objects.filter(author__following__user=follow).order_by("-pub_date").all()

    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)

    return render(request, "follow.html", {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    follower = get_object_or_404(User, username=request.user.username) #  кто подписывается
    follow = get_object_or_404(User, username=username) #  на кого подписывается

    if follower != follow:

        uniq = Follow.objects.filter(user=follower, author=follow).count()
        if uniq:
            return redirect ('posts:profile', username=username)
        Follow.objects.create(user=follower, author=follow)
        
    return redirect ('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = User.objects.get(username=request.user.username) #  кто отписывается
    unfollow = User.objects.get(username=username) #  от кого отписывается
    
    Follow.objects.filter(user=follower, author=unfollow).delete()

    return redirect('posts:profile', username=username)