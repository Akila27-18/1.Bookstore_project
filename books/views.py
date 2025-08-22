from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Avg


from .models import Book, Author, Category, Review
from .forms import SearchForm, ReviewForm, RegisterForm
from .filters import filter_books


# --- Basics (FBV) ---


def home(request):
    ctx = {
        'form': SearchForm(request.GET or None),
    }
    return render(request, 'books/home.html', ctx)




def about(request):
    return render(request, 'books/about.html')


# --- Auth ---


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'books/auth/register.html', {'form': form})


# --- Books (CBV) ---


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 10


    def get_queryset(self):
        qs = Book.objects.select_related('author').prefetch_related('categories').all()
        q = self.request.GET.get('q', '').strip()
        author_id = self.request.GET.get('author')
        category_slug = self.request.GET.get('category')
        qs = filter_books(qs, q=q, author_id=author_id, category_slug=category_slug)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = SearchForm(self.request.GET or None)
        ctx['authors'] = Author.objects.all()
        ctx['categories'] = Category.objects.all()
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_author'] = self.request.GET.get('author', '')
        ctx['selected_category'] = self.request.GET.get('category', '')
        return ctx
class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'


    # Requirement: use get_object_or_404() for book detail pages
    def get_object(self, queryset=None):
        return get_object_or_404(Book.objects.select_related('author').prefetch_related('categories', 'reviews__user'), pk=self.kwargs['pk'])


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        book = self.object
        ctx['avg_rating'] = book.reviews.filter(approved=True).aggregate(avg=Avg('rating'))['avg']
        ctx['reviews'] = book.reviews.filter(approved=True)
        ctx['can_review'] = self.request.user.is_authenticated and not book.reviews.filter(user=self.request.user).exists()
        ctx['review_form'] = ReviewForm()
        return ctx
# --- Reviews (CBV) ---
class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        review = self.get_object()
        return review.user == self.request.user


from django.core.mail import send_mail
from django.conf import settings

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'books/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.book = get_object_or_404(Book, pk=self.kwargs['book_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = self.book
        messages.success(self.request, 'Review submitted! It will appear once approved.')

        response = super().form_valid(form)

        # 📧 Send email notification
        try:
            send_mail(
                subject=f"New review submitted for {self.book.title}",
                message=(
                    f"User {self.request.user.username} submitted a review.\n\n"
                    f"Rating: {form.instance.rating}\n"
                    f"Comment: {form.instance.comment}\n\n"
                    f"Book: {self.book.title}\nAuthor: {self.book.author.name}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["your_email@gmail.com"],  # change to admin/author email
                fail_silently=False,
            )
        except Exception as e:
            print("⚠️ Email not sent:", e)

        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['book'] = self.book
        return ctx



class ReviewUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'books/review_form.html'


    def form_valid(self, form):
        messages.success(self.request, 'Review updated! Pending approval if changed.')
        # If users edit, re-set approved to False for moderation (optional)
        form.instance.approved = False
        return super().form_valid(form)


class ReviewDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Review
    template_name = 'books/review_confirm_delete.html'


    def get_success_url(self):
        messages.info(self.request, 'Your review was deleted.')
        return self.object.book.get_absolute_url()
