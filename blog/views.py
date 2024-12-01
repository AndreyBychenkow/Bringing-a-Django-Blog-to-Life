import folium
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.dateformat import format

from blog.models import Comment
from blog.models import Post
from sensive_blog.settings import COMPANY_COORDINATES


def serialize_post(post):
    return {
        'title': post.title,
        'description': post.text,
        'image_url': post.image.url if post.image else '/static/images/banner/blog.png',
        'published_date': format(post.published_at, 'F j, Y, g:i a'),
        'author': post.author.username,
        'comments_count': post.comment_set.count(),
        'url': post.get_absolute_url(),
    }


def index(request):
    most_popular_posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:3]

    fresh_posts = Post.objects.order_by('-published_at')[:5]

    context = {
        'most_popular_posts': most_popular_posts,
        'fresh_posts': fresh_posts,
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = Comment.objects.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        'likes_amount': post.likes.count(),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
    }

    context = {
        'post': serialized_post,
    }
    return render(request, 'blog-details.html', context)


def contact(request):

    folium_map = folium.Map(location=COMPANY_COORDINATES, zoom_start=12)
    folium.Marker(
        COMPANY_COORDINATES,
        tooltip="Мы здесь",
    ).add_to(folium_map)
    html_map = folium_map._repr_html_()
    return render(request, 'contact.html', {"html_map": html_map})
