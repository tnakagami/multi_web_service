from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy
from websocket import create_connection
from websocket._exceptions import WebSocketTimeoutException, WebSocketConnectionClosedException
import requests
import json

class AccessToken(models.Model):
    # token
    access_token = models.CharField(ugettext_lazy('access token'), max_length=128)
    # create time
    created_at = models.DateTimeField(ugettext_lazy('create time'), default=timezone.now)

    def is_valid_access_token(self, token):
        return self.access_token == token

    def get_reqres(self, url):
        # send GET request
        response = requests.get(url)

        return response.text

    def websocket_communication(self, url, data):
        # open connection
        ws_conn = create_connection(url, timeout=4.25)
        try:
            # send request to websocket server
            ws_conn.send(data)
            # receive response from websocket server
            response = ws_conn.recv()
            # close connection
        except (WebSocketTimeoutException, WebSocketConnectionClosedException) as e:
            response = json.dumps({'status_code': 500, 'message': 'Internal Server Error ({})'.format(e)})
        ws_conn.close()

        return json.loads(response)

    def short_token(self):
        return '{}...'.format(self.access_token[:10])
    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return self.access_token
