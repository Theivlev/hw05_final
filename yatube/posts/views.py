from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User
from .utilits import get_pages_paginator


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.select_related('group')
    page_obj = get_pages_paginator(request, posts, Post.OUTPUT_OF_POSTS)
    context = {
        'posts': posts,
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:Post.OUTPUT_OF_POSTS]
    page_obj = get_pages_paginator(request, posts, Post.OUTPUT_OF_POSTS)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


class JustStaticPage(TemplateView):
    template_name = 'app_name/just_page.html'


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    subscriber = request.user
    profile_list = Post.objects.filter(author=author)
    following = subscriber.is_authenticated and Follow.objects.filter(
        user=subscriber,
        author=author
    )
    count_posts = profile_list.count()
    page_obj = get_pages_paginator(request, profile_list, Post.OUTPUT_OF_POSTS)
    context = {
        'author': author,
        'profile_list': profile_list,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'following': following

    }

    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    comment = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comment,
    }

    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    subscriber = request.user
    follow_author = Post.objects.filter(author__following__user=subscriber)
    page_obj = get_pages_paginator(
        request, follow_author, Post.OUTPUT_OF_POSTS)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author and not Follow.objects.filter(
        user=user, author=author
    ).exists():
        Follow.objects.create(
            user=user,
            author=author,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    subscriber = request.user
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=subscriber, author=author)
    follow.delete()
    return redirect('posts:index')
