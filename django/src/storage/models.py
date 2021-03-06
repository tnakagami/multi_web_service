from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy
import os

User = get_user_model()

def get_filepath(instance, filename):
    return os.path.join(instance.user.username, filename)

class FileStorage(models.Model):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # file storage
    file = models.FileField(
        upload_to=get_filepath,
        verbose_name=ugettext_lazy('upload file'),
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png', 'txt', 'md', 'zip'])],
        blank=False,
    )
    # create time
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.filename()
    def filename(self):
        return os.path.basename(self.file.name)
