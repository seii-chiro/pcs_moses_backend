from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum

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
    is_voter = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=UserStatus.choices(),
        default=UserStatus.NEW.value,
    )
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    date_paid_billed = models.DateField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    partner_or_individual = models.CharField(
        max_length=50, null=True, blank=True)
    month_year_entered = models.CharField(max_length=7, null=True, blank=True)
    anniversary_month = models.CharField(max_length=3, null=True, blank=True)
    title = models.CharField(max_length=20)
    member = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)
    allow_proxy = models.BooleanField(default=False)

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        VOTER = "voter", "Voter"
        ELECOM = "elecom", "Elecom"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VOTER,
    )

    def save(self, *args, **kwargs):
        # Check if the password is not hashed and only then hash it
        if self.pk and self.password and not self.password.startswith('pbkdf2'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} {self.first_name} {self.last_name}'
