from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import EmailField
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    phone = CharField(_("phone"), unique=True, max_length=15, blank=True)
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    is_verified = BooleanField(default=False)

    objects: ClassVar[UserManager] = UserManager()

    def __str__(self):
        return self.email
