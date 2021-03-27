import datetime
import pytz
from django.conf import settings
from django.utils import timezone
from factory import LazyAttribute, Sequence, post_generation
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDateTime
from chat import models

tzinfo = pytz.timezone(settings.TIME_ZONE)

class RoomFactory(DjangoModelFactory):
    class Meta:
        model = models.Room

    name = Sequence(lambda count: 'chat_room{}'.format(count))
    description = LazyAttribute(lambda instance: '{}_description'.format(instance.name))
    created_at = FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))

    @post_generation
    def assigned(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for _user in extracted:
                self.assigned.add(_user)

class MessageFactory(DjangoModelFactory):
    class Meta:
        model = models.Message

    content = Sequence(lambda count: 'content{}'.format(count))
    created_at = FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))
