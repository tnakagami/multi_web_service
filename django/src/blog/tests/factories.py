import datetime
import pytz
from django.conf import settings
from django.utils import timezone
from factory import LazyAttribute, Sequence, post_generation
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDateTime
from blog import models

tzinfo = pytz.timezone(settings.TIME_ZONE)

class TagFactory(DjangoModelFactory):
    class Meta:
        model = models.Tag

    name = Sequence(lambda count: 'tag{}'.format(count))

class PostFactory(DjangoModelFactory):
    class Meta:
        model = models.Post

    title = Sequence(lambda count: 'title{}'.format(count))
    text = Sequence(lambda count: '# post text\ntext {}'.format(count))
    is_public = True
    description = LazyAttribute(lambda instance: '{}_description'.format(instance.title))
    keywords = LazyAttribute(lambda instance: '{}_keyword'.format(instance.title))
    created_at = FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))
    updated_at =  FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))

    @post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)

    @post_generation
    def relation_posts(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for post in extracted:
                self.relation_posts.add(post)

class CommentFactory(DjangoModelFactory):
    class Meta:
        model = models.Comment

    name = Sequence(lambda count: 'comment{}'.format(count))
    text = Sequence(lambda count: '# comment text\ncomment {}'.format(count))
    created_at = FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))

class ReplyFactory(DjangoModelFactory):
    class Meta:
        model = models.Reply

    name = Sequence(lambda count: 'reply{}'.format(count))
    text = Sequence(lambda count: '# reply text\nreply {}'.format(count))
    created_at = FuzzyDateTime(start_dt=timezone.datetime(2021, 1, 1, tzinfo=tzinfo))
