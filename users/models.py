from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum
from django.utils import timezone
from django.conf import settings


class Vote(models.Model):
    voted_at = models.DateTimeField(null=True, blank=True)
    voter_id = models.IntegerField(default=0)
    proxy_for_voter_id = models.IntegerField(default=0)
    candidate_id = models.IntegerField(default=0)
    notes = models.TextField(default='', blank=True)
    is_counted = models.BooleanField(default=False)
    counted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    record_status_id = models.IntegerField(default=1)

    class Meta:
        db_table = 'votes'

    def __str__(self):
        return f"Vote #{self.id} by Voter {self.voter_id}"


class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)
    role_level = models.IntegerField()
    description = models.TextField()
    notes = models.TextField(blank=True, null=True)

    # or ForeignKey to user if needed
    created_by = models.CharField(max_length=50, default="system")
    updated_by = models.CharField(max_length=50, default="system")  # same here

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Assuming you have a RecordStatus model; if not, just use an IntegerField or ForeignKey
    record_status_id = models.IntegerField(default=1)

    def __str__(self):
        return self.role_name


# User status enum
class UserStatus(Enum):
    NEW = "NEW"
    BALIK_PCS = "BALIK_PCS"
    RENEWED = "RENEWED"
    RE_MEMBER = "RE_MEMBER"
    CURRENT_BOT = "CURRENT_BOT"

    @classmethod
    def choices(cls):
        return [(tag.value, tag.value) for tag in cls]


# Custom user model
class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    allow_proxy = models.BooleanField(default=False)
    requested_proxy = models.JSONField(default=list, blank=True)
    received_proxy_requests = models.JSONField(default=list, blank=True)
    voted_at = models.DateTimeField(null=True, blank=True)
    voted_longitude = models.FloatField(null=True, blank=True)
    voted_latitude = models.FloatField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.CharField(max_length=50, default="system")
    updated_by = models.CharField(max_length=50, default="system")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    record_status_id = models.IntegerField(default=1)
    proxy_id = models.IntegerField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    image_base64 = models.TextField(null=True, blank=True)
    started_voting = models.DateTimeField(null=True, blank=True)
    finished_voting = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Extract update_password parameter or default to True
        update_password = kwargs.pop('update_password', True)

        # Generate full_name if not provided
        if not self.full_name and (self.first_name or self.last_name):
            title_part = f"{self.title} " if self.title else ""
            first_part = f"{self.first_name} " if self.first_name else ""
            middle_initial = f"{self.middle_name[0]}. " if self.middle_name else ""
            self.full_name = f"{title_part}{first_part}{middle_initial}{self.last_name}".strip(
            )

        # Check if the password is not hashed and only then hash it
        if update_password and self.pk and self.password and not self.password.startswith('pbkdf2') and not self.password.startswith('argon2'):
            self.set_password(self.password)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} {self.first_name} {self.last_name}'

    def has_max_accepted_proxies(self):
        """Returns True if the user has 1 accepted proxy, otherwise False."""
        return len([p for p in self.requested_proxy if p.get('status') == 'accepted']) >= 1
