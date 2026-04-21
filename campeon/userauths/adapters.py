from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self,request,sociallogin):
        user = sociallogin.user
        extra_data =  sociallogin.account.extra_data
        email = extra_data.get('email')
        if email:
            try:
                existing_user = User.objects.get(email = email)
                sociallogin.connect(request,existing_user)
                return
            except User.DoesNotExist:
                pass

        if sociallogin.account.provider == 'google':
            user.is_active = True
            name = extra_data.get('name')
            if not user.full_name :
                user.full_name=extra_data.get('name','')
            user.username = email.split("@")[0]
            user.save()
