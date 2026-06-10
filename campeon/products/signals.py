from django.dispatch import receiver
from .models import Wallet
from user.models import Account
from django.db.models.signals import post_save


@receiver(post_save, sender=Account)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
