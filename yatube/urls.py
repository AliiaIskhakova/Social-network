
from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # раздел администратора
    path("admin/", admin.site.urls),

    # flatpages
    path("about/", include("django.contrib.flatpages.urls")),

    # регистрация и авторизация
    path("auth/", include("users.urls")),

    # если нужного шаблона для /auth не нашлось в файле users.urls — 
    # ищем совпадения в файле django.contrib.auth.urls
    path("auth/", include("django.contrib.auth.urls")),

    # обработчик для главной страницы ищем в urls.py приложения posts
    path("", include("posts.urls")),

    path("404/", handler404),
    path("500/", handler500),

]

urlpatterns += [
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='about-author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='about-spec'),
]

handler404 = "posts.views.page_not_found"
handler500 = "posts.views.server_error"

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
