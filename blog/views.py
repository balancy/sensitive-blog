from django.shortcuts import render
from blog.models import Post, Tag


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag':
            tag.posts_count if hasattr(tag, 'posts_count') else 0,
    }


def serialize_post(post):
    post_tags = [serialize_tag(tag) for tag in post.tags.all()]
    return {
        'title': post.title,
        'author': post.author.username,
        'image_url': image.url if (image := post.image) else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'first_tag_title': post_tags[0]['title'],
        'teaser_text': post.text[:200],
        'comments_amount':
            post.comments_count if hasattr(post, 'comments_count') else 0,
        'tags': post_tags,
    }


def index(request):
    all_posts = Post.objects \
        .prefetch_related('tags') \
        .prefetch_related('author')

    most_popular_posts = all_posts.popular()[:5]

    fresh_posts = \
        all_posts.fetch_with_comments_count().order_by('-published_at')[:5]

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts':
            [serialize_post(post) for post in most_popular_posts],
        'page_posts':
            [serialize_post(post) for post in fresh_posts],
        'popular_tags':
            [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = post.comments.prefetch_related('author')

    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': len(likes),
        'image_url': image.url if (image := post.image) else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    all_posts = Post.objects.prefetch_related('author')
    most_popular_posts = all_posts.popular()[:5]

    context = {
        'post': serialized_post,
        'popular_tags':
            [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts':
            [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)
    most_popular_tags = Tag.objects.popular()[:5]

    all_posts = Post.objects.prefetch_related('author')
    most_popular_posts = all_posts.popular()[:5]

    related_posts = \
        tag.posts.prefetch_related('author') \
        .prefetch_related('tags') \
        .fetch_with_comments_count()[:20]

    context = {
        'tag': tag.title,
        'popular_tags':
            [serialize_tag(tag) for tag in most_popular_tags],
        'posts':
            [serialize_post(post) for post in related_posts],
        'most_popular_posts':
            [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
