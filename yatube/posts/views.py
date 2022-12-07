from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page
from .forms import PostForm, CommentForm
from .models import Post, Group, Follow
from .utils import pagination


MAX_POSTS_VISIBLE = 10  # the number of posts you'll see on page
MAX_POST_CHARS = 30  # the amount of text displayed
User = get_user_model()


@cache_page(20, cache='default', key_prefix='index_page')
def index(request):
    """Start page for posts app."""
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    title = 'Последние обновления на сайте'
    context = {
        'title': title,
        'posts': posts,
        'page_obj': pagination(request, posts, MAX_POSTS_VISIBLE),
    }
    return render(request, template, context)


def group_posts(request, slug):
    """List of posts by certain group."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    title = f'Записи сообщества {group.title}'
    context = {
        'title': title,
        'group': group,
        'posts': posts,
        'page_obj': pagination(request, posts, MAX_POSTS_VISIBLE),
    }
    return render(request, template, context)


def profile(request, username):
    """Calls page with user's profile."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    title = f'Профиль пользователя {author.get_full_name()}'
    posts = author.posts.select_related('author', 'group')
    total_posts = posts.count()
    following = False
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    context = {
        'title': title,
        'author': author,
        'page_obj': pagination(request, posts, MAX_POSTS_VISIBLE),
        'total_posts': total_posts,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Expands post information."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        id=post_id
    )
    comments = post.comments.select_related('post')
    form = CommentForm()
    title = f'Пост {post.text[:MAX_POST_CHARS]}'
    total_posts = post.author.posts.count()
    context = {
        'title': title,
        'posts': post,
        'total_posts': total_posts,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Creates a new post."""
    template = 'posts/create_post.html'
    title = 'Новая запись в блоге.'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)
    context = {
        'title': title,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Edits an existing post."""
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/create_post.html'
    title = 'Редактирование записи'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    elif request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    context = {
        'title': title,
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Adds comment to a post."""
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    title = f'Лента подписок пользователя {request.user.get_full_name()}'
    context = {
        'title': title,
        'posts': posts,
        'page_obj': pagination(request, posts, MAX_POSTS_VISIBLE),
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Starts following other user."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        if author.following.exists():
            return redirect('posts:profile', username)
        Follow.objects.create(user=request.user, author=author)
        return redirect('posts:profile', username)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Ceases following other user."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
