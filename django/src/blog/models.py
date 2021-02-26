from django.db import models
from django.utils import timezone

class Tag(models.Model):
    """
    tag
    """
    name = models.CharField('tag name', max_length=255, unique=True)

    def __unicode__(self):
        return self.name

class Post(models.Model):
    """
    post
    """
    # title
    title = models.CharField('title', max_length=64)
    # body text
    text = models.TextField('body text')
    # tag information
    tags = models.ManyToManyField(Tag, verbose_name='tag', blank=True)
    # relation post
    relation_posts = models.ManyToManyField('self', verbose_name='relation_posts', blank=True)
    # is public
    is_public = models.BooleanField('public or private', default=True)
    # description
    description = models.TextField('description', max_length=128)
    # keyword
    keywords = models.CharField('post keyword', max_length=255, default='default keyword')
    # create time
    created_at = models.DateTimeField('create time', default=timezone.now)
    # update time
    updated_at = models.DateTimeField('update time', default=timezone.now)

    def __unicode__(self):
        return self.title

class Comment(models.Model):
    """
    comment
    """
    # name
    name = models.CharField('name', max_length=255, default='no name')
    # comment text
    text = models.TextField('comment')
    # target post
    target = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='target post')
    # create time
    created_at = models.DateTimeField('create time', default=timezone.now)

    def __unicode__(self):
        return self.comment_text[:32]

class Reply(models.Model):
    """
    reply to comment
    """
    # name
    name = models.CharField('name', max_length=255, default='no name')
    # reply text
    text = models.TextField('reply text')
    # target comment
    target = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='target comment')
    # create time
    created_at = models.DateTimeField('create time', default=timezone.now)

    def __str__(self):
        return self.text[:20]
