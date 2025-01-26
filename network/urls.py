
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("posts", views.posts, name="posts"),
    path("posts/<str:pick>", views.pick, name="pick"),
    path("posts/edit/<int:edit>", views.edit, name="edit"),
    path("posts/like/<int:id_post>", views.like, name="like"),
    path("follow/<str:username>", views.follow, name="follow"),
    path("numbers/<str:username>", views.numbers, name="numbers"),
]
