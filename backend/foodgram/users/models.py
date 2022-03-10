from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    username = models.CharField(db_index=True, max_length=255, unique=True)

    first_name = models.CharField(db_index=True, max_length=255,)

    last_name = models.CharField(db_index=True, max_length=255,)

    email = models.EmailField(db_index=True, unique=True)

    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, USER),
        (ADMIN, ADMIN),
    ]
    role = models.CharField(
        'role',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', ],
                name='unique_username'
            ),
            models.UniqueConstraint(
                fields=['email', ],
                name='unique_email'
            ),
            models.CheckConstraint(
                check=~Q(username__iexact='me'),
                name='cant_given_username'
            ),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN
