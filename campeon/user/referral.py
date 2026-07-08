from userauths.models import Account
from products.models import Wallet, WalletTransaction
from django.db import transaction

# Referrer (person whose code was used) → ₹10
# Referred user (new user applying the code) → ₹5


referred_user_bonus_amount = 5

referral_bonus_amount = 10


def apply_referral_bonus(user, referral_code):
    if not referral_code:
        return

    try:
        referred_user = Account.objects.get(referral_code=referral_code)
    except Account.DoesNotExist:
        return

    if referred_user == user:
        return

    if user.referred_by_id:
        return  # already applied

    with transaction.atomic():
        user.referred_by = referred_user
        user.save(update_fields=["referred_by"])

        # Give ₹10 to referrer
        referred_user.referral_count = (referred_user.referral_count or 0) + 1
        referred_user.total_referral_amount = (
            referred_user.total_referral_amount or 0
        ) + referral_bonus_amount
        referred_user.save(update_fields=["referral_count", "total_referral_amount"])

        wallet, _ = Wallet.objects.get_or_create(user=referred_user)
        wallet.current_balance += referral_bonus_amount
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=referral_bonus_amount,
            source="referral",
            transaction_type="credit",
        )
        # Give ₹5 to new user

        user_wallet, _ = Wallet.objects.get_or_create(user=user)

        user_wallet.current_balance = (
            user_wallet.current_balance or 0
        ) + referred_user_bonus_amount
        user_wallet.save()

        WalletTransaction.objects.create(
            wallet=user_wallet,
            amount=referred_user_bonus_amount,
            source="referral_bonus",
            transaction_type="credit",
        )
