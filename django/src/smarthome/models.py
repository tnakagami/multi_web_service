from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy
import requests
import json

class AccessToken(models.Model):
    # token
    access_token = models.CharField(ugettext_lazy('access token'), max_length=128)
    # create time
    created_at = models.DateTimeField(ugettext_lazy('create time'), default=timezone.now)

    def is_valid_access_token(self, token):
        return self.access_token == token

    def post_request(self, url, data):
        # send POST request
        response = requests.post(url, data=data)
        # check status code
        if response.status_code != 200:
            raise response.raise_for_status()

        return json.loads(response.text)

    def short_token(self):
        return '{}...'.format(self.access_token[:10])
    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.access_token
