import datetime
import pytz
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from factory import LazyAttribute, Sequence
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDateTime

tzinfo = pytz.timezone(settings.TIME_ZONE)
UserModel = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = UserModel

    username = Sequence(lambda count: 'user{}'.format(count))
    viewname = Sequence(lambda count: 'viewname{}'.format(count))
    password = make_password('password')
    email = LazyAttribute(lambda instance: '{}@example.com'.format(instance.username))
    is_staff = False
    is_active = True
    date_joined = FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))
