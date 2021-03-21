import datetime
import pytz
from django.conf import settings
from django.utils import timezone
from factory import Sequence
from factory.django import DjangoModelFactory, FileField
from factory.fuzzy import FuzzyDateTime
from storage import models

tzinfo = pytz.timezone(settings.TIME_ZONE)

class FileStorageFactory(DjangoModelFactory):
    class Meta:
        model = models.FileStorage

    filename = Sequence(lambda count: 'filename{}.txt'.format(count))
    file = FileField(filename=Sequence(lambda count: 'filename{}.txt'.format(count)))
    created_at = FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))
