
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
# Basic pages (FBV)
path('', views.home, name='home'),
path('about/', views.about, name='about'),


# Auth
path('login/', auth_views.LoginView.as_view(template_name='books/auth/login.html'), name='login'),
path('logout/', auth_views.LogoutView.as_view(template_name='books/auth/logout.html'), name='logout'),
path('register/', views.register, name='register'),


# Books (CBV + DetailView uses get_object_or_404 internally)
path('books/', views.BookListView.as_view(), name='book-list'),
path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),


# Reviews CRUD (CBV)
path('books/<int:book_id>/reviews/add/', views.ReviewCreateView.as_view(), name='review-add'),
path('reviews/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review-edit'),
path('reviews/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
]
