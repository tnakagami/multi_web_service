from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy
import os
import hashlib
from datetime import datetime

User = get_user_model()

def get_filepath(instance, filename):
    current_time = datetime.now()
    pre_hash_value = '{}{}{}'.format(instance.user.id, filename, current_time)
    extension = str(filename).split('.')[-1]
    hashed_filename = '{}.{}'.format(hashlib.md5(pre_hash_value.encode()).hexdigest(), extension)

    return os.path.join(instance.user.username, hashed_filename)

class FileStorage(models.Model):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # filename
    filename = models.CharField(max_length=255)
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
        return self.filename
