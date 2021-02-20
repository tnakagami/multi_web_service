from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy, ugettext_lazy
import re

@deconstructible
class CustomASCIIUsernameValidator(validators.RegexValidator):
    regex = r'^\w+$'
    message = gettext_lazy(
        'Enter a valid username. This value may contain only English letters, '
        'numbers, and _ characters.'
    )
    flags = re.ASCII

class CustomUserManager(UserManager):
    """
    Custom User Manager
    """

    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        if not email:
            raise ValueError('The given email must be set')
        username = self.model.normalize_username(username)
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, email, password,  **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password,  **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User
    """
    username_validator = CustomASCIIUsernameValidator()

    username = models.CharField(
        ugettext_lazy('username'),
        max_length=128,
        unique=True,
        help_text=ugettext_lazy('Required. 128 characters or fewer. Letters, digits and _ only.'),
        validators=[username_validator],
        error_messages={
            'unique': ugettext_lazy("A user with that username already exists."),
        },
    )
    viewname = models.CharField(
        ugettext_lazy('view name'),
        max_length=128,
        blank=True,
        help_text=ugettext_lazy('Required. 128 characters or fewer.'),
    )
    email = models.EmailField(ugettext_lazy('email address'), unique=True)
    is_staff = models.BooleanField(
        ugettext_lazy('staff status'),
        default=False,
        help_text=ugettext_lazy('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        ugettext_lazy('active'),
        default=True,
        help_text=ugettext_lazy(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(ugettext_lazy('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = ugettext_lazy('user')
        verbose_name_plural = ugettext_lazy('users')

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return self.username

    def get_short_name(self):
        """Return the short name for the user."""
        return self.get_full_name()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
