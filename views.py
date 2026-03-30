from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm, ProfileForm, RegisterForm
from .models import Follow, Like, Post, Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def home_view(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created.')
            return redirect('home')
    else:
        post_form = PostForm()

    followed_users = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    posts = Post.objects.filter(Q(user__in=followed_users) | Q(user=request.user)).select_related('user', 'user__profile')
    liked_post_ids = set(
        Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True)
    )

    context = {
        'posts': posts,
        'post_form': post_form,
        'comment_form': CommentForm(),
        'liked_post_ids': liked_post_ids,
    }
    return render(request, 'core/home.html', context)


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=profile_user)

    if request.method == 'POST' and request.user == profile_user:
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile', username=profile_user.username)
    else:
        form = ProfileForm(instance=profile)

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'form': form,
        'posts': profile_user.posts.all(),
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
        'is_following': is_following,
    }
    return render(request, 'core/profile.html', context)


@login_required
def toggle_like_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def add_comment_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def toggle_follow_view(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user != request.user:
        relation, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
        if not created:
            relation.delete()
    return redirect('profile', username=target_user.username)
