from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator

User = get_user_model()

class Tweet(models.Model):
    # if reference user is deleted, related tweets also are deleted.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # tweet text
    text = models.TextField(validators=[MinLengthValidator(1), MaxLengthValidator(140)])
    # create time
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.text

class Relationship(models.Model):
    # follower relationship as seen by the user
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relationship_owner')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relationship_follower')

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return '{}-{}'.format(self.owner.username, self.follower.username)
