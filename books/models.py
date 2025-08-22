from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Author(models.Model):
    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)


    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    categories = models.ManyToManyField(Category, related_name='books', blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    published_date = models.DateField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['title']


    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse('book-detail', args=[self.pk])


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False) # for moderation


    class Meta:
        unique_together = ('book', 'user') # one review per user per book (optional)
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.user.username} → {self.book.title} ({self.rating})"


    def get_absolute_url(self):
        return self.book.get_absolute_url()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)


    def __str__(self):
        return self.display_name or self.user.username
