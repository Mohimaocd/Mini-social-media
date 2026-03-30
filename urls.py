from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    add_comment_view,
    home_view,
    profile_view,
    register_view,
    toggle_follow_view,
    toggle_like_view,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/<str:username>/', profile_view, name='profile'),
    path('posts/<int:post_id>/like/', toggle_like_view, name='toggle_like'),
    path('posts/<int:post_id>/comment/', add_comment_view, name='add_comment'),
    path('follow/<str:username>/', toggle_follow_view, name='toggle_follow'),
]
