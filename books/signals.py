from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile, Review


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, display_name=instance.username)


# Email when a review is approved (transition from False → True)
@receiver(pre_save, sender=Review)
def email_on_review_approved(sender, instance, **kwargs):
    if not instance.pk:
        return # only on updates
    try:
        previous = Review.objects.get(pk=instance.pk)
    except Review.DoesNotExist:
        return
    if not previous.approved and instance.approved:
        # Send email after save using post_save? We can send here as well.
        # Using send_mail with console backend in dev.
        subject = f"Your review for '{instance.book.title}' was approved"
        message = (
            f"Hi {instance.user.username},\n\n"
            f"Your review (rating: {instance.rating}) for '{instance.book.title}' has been approved.\n"
            f"You can view it here: {settings.DEFAULT_FROM_EMAIL}"
        )
        recipient = [instance.user.email] if instance.user.email else []
        if recipient:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient, fail_silently=True)
        