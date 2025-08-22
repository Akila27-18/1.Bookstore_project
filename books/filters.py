from django.db.models import Q
from .models import Book


def filter_books(queryset, q=None, author_id=None, category_slug=None):
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(author__name__icontains=q) |
            Q(categories__name__icontains=q)
        ).distinct()
    if author_id:
        queryset = queryset.filter(author_id=author_id)
    if category_slug:
        queryset = queryset.filter(categories__slug=category_slug)
    return queryset
