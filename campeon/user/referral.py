from userauths.models import Account
from products.models import Wallet,WalletTransaction
from django.db import transaction



referral_code_amount = 10
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
        
        referred_user.referral_count = (referred_user.referral_count or 0) + 1
        referred_user.total_referral_amount = (referred_user.total_referral_amount or 0) + referral_code_amount
        referred_user.save(update_fields=["referral_count", "total_referral_amount"])

        wallet, _ = Wallet.objects.get_or_create(user=referred_user)
        wallet.current_balance += referral_code_amount
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=referral_code_amount,
            source="referral_bonus",
            transaction_type="credit",
        )

