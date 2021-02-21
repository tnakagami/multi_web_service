from django.core import mail, management
from django.core.urlresolvers import reverse, resolve
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from . import views, forms, models

User = get_user_model()

