from .models import Wallet, WalletTransaction
from django.db import transaction


class WalletService:
    @staticmethod
    def debit_wallet(user, amount, order=None):

        wallet = Wallet.objects.get(user=user)
        if wallet.current_balance < amount:
            raise ValueError("Insufficient Balance")
        with transaction.atomic():
            wallet.current_balance -= amount
            wallet.save()
            WalletTransaction.objects.create(
                order=order,
                wallet=wallet,
                amount=amount,
                source="order_payment",
                transaction_type="debit",
            )

    @staticmethod
    def credit_wallet(user, amount, order=None, source="refund"):
        wallet = Wallet.objects.get(user=user)
        with transaction.atomic():
            wallet.current_balance += amount
            wallet.save()
            WalletTransaction.objects.create(
                order=order,
                wallet=wallet,
                amount=amount,
                source=source,
                transaction_type="credit",
            )
