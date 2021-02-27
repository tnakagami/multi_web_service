from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy

User = get_user_model()

class Tag(models.Model):
    """
    tag
    """
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # tag name
    name = models.CharField(ugettext_lazy('tag name'), max_length=255, unique=True)

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.name

class Post(models.Model):
    """
    post
    """
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # title
    title = models.CharField(ugettext_lazy('title'), max_length=64)
    # body text
    text = models.TextField(ugettext_lazy('body text'))
    # tag information
    tags = models.ManyToManyField(Tag, verbose_name=ugettext_lazy('tag'), blank=True)
    # relation post
    relation_posts = models.ManyToManyField('self', verbose_name=ugettext_lazy('relation posts'), blank=True)
    # is public
    is_public = models.BooleanField(ugettext_lazy('public or private'), default=True)
    # description
    description = models.TextField(ugettext_lazy('description'), max_length=128)
    # keyword
    keywords = models.CharField(ugettext_lazy('post keyword'), max_length=255, default='')
    # create time
    created_at = models.DateTimeField(ugettext_lazy('create time'), default=timezone.now)
    # update time
    updated_at = models.DateTimeField(ugettext_lazy('update time'), default=timezone.now)

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.title

class Comment(models.Model):
    """
    comment
    """
    # name
    name = models.CharField(ugettext_lazy('name'), max_length=255, default='no name')
    # comment text
    text = models.TextField(ugettext_lazy('comment'))
    # target post
    target = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name=ugettext_lazy('target post'))
    # create time
    created_at = models.DateTimeField(ugettext_lazy('create time'), default=timezone.now)

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.comment_text[:32]

class Reply(models.Model):
    """
    reply to comment
    """
    # name
    name = models.CharField(ugettext_lazy('name'), max_length=255, default='no name')
    # reply text
    text = models.TextField(ugettext_lazy('reply text'))
    # target comment
    target = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name=ugettext_lazy('target comment'))
    # create time
    created_at = models.DateTimeField(ugettext_lazy('create time'), default=timezone.now)

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.text[:20]
