from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
            ret_val = user if user.check_password(password) and self.user_can_authenticate(user) else None
        except User.DoesNotExist:
            ret_val = None
        except MultipleObjectsReturned:
            user = User.objects.filter(email=username).order_by('id').first()
            ret_val = user if user.check_password(password) and self.user_can_authenticate(user) else None

        return ret_val

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            ret_val = user if self.user_can_authenticate(user) else None
        except User.DoesNotExist:
            ret_val = None

        return ret_val
