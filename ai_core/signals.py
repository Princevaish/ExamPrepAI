from allauth.account.signals import user_signed_up
from django.dispatch import receiver
import uuid


@receiver(user_signed_up)
def set_username(sender, request, user, **kwargs):
    """
    Ensures every user has a unique username.
    Required for PostgreSQL compatibility.
    """
    if not user.username:
        user.username = f"user_{uuid.uuid4().hex[:10]}"
        user.save()
