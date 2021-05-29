import datetime
import pytz
from django.conf import settings
from django.utils import timezone
from factory import Sequence
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDateTime
from smarthome import models

tzinfo = pytz.timezone(settings.TIME_ZONE)

class AccessTokenFactory(DjangoModelFactory):
    class Meta:
        model = models.AccessToken

    access_token = Sequence(lambda count: 'access2token{}'.format(count))
    created_at = FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))
