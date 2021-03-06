from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy

User = get_user_model()

class Room(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(ugettext_lazy('name'), max_length=64)
    description = models.TextField(ugettext_lazy('description'), max_length=128)
    assigned = models.ManyToManyField(User, related_name='room_assigned', verbose_name=ugettext_lazy('assigned users'), blank=True)
    created_at = models.DateTimeField(ugettext_lazy('create time'), default=timezone.now)

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.name
    def is_assigned(self, user):
        try:
            _ = self.assigned.all().get(pk=user.pk)
            ret = True
        except User.DoesNotExist:
            ret = self.owner.pk == user.pk

        return ret

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.TextField(ugettext_lazy('content'))
    created_at = models.DateTimeField(ugettext_lazy('create time'), default=timezone.now)

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return '{}: {}'.format(self.user.username, self.content[:32])
