from django.shortcuts import render
from blog.models import Post, Tag


def serialize_tag_in_post(tag):
    return {
        'title': tag.title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def serialize_popular_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'first_tag_title': post.tags.first().title,
    }


def serialize_fresh_post(post):
    fresh_post = serialize_popular_post(post)
    fresh_post.update({
        'comments_amount': post.comments_count if post.comments_count else None,
        'tags': [serialize_tag_in_post(tag) for tag in post.tags.all()],
    })
    return fresh_post


def index(request):
    all_posts = Post.objects.prefetch_related('author').prefetch_related('tags')
    most_popular_posts = all_posts.popular()[:5]
    most_fresh_posts = all_posts.fresh(5).fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_popular_post(post) for post in most_popular_posts],
        'page_posts': [serialize_fresh_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = post.comments.all()

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
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    popular_tags = Tag.objects.filter(posts=post).popular()
    most_popular_tags = popular_tags[:5]

    all_posts = Post.objects.prefetch_related('author')
    most_popular_posts = all_posts.popular()[:5]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_popular_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    popular_tags = Tag.objects.popular()
    most_popular_tags = popular_tags[:5]

    all_posts = Post.objects.prefetch_related('author')
    most_popular_posts = all_posts.popular()[:5]

    related_posts = tag.posts.all()
    related_posts_ids = [post.id for post in related_posts[:20]]
    most_related_posts = related_posts.filter(id__in=related_posts_ids).fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_fresh_post(post) for post in most_related_posts],
        'most_popular_posts': [serialize_popular_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
