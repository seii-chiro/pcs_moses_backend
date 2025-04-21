from django.db import models

from django.db import models
from django.utils import timezone

class Election(models.Model):
    organization = models.CharField(max_length=255)
    election_name = models.CharField(max_length=255)
    voting_start = models.DateTimeField()
    voting_end = models.DateTimeField()
    no_slots = models.PositiveIntegerField(default=0)
    no_ballots = models.PositiveIntegerField(default=0)
    poll_open_at = models.DateTimeField(null=True, blank=True)
    poll_closed_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_poll_open(self):
        now = timezone.now()
        return self.voting_start <= now <= self.voting_end

    @property
    def is_poll_closed(self):
        now = timezone.now()
        return now > self.voting_end

    def __str__(self):
        return self.election_name

class Position(models.Model):
    description = models.CharField(max_length=255)
    email = models.EmailField()
    member = models.CharField(max_length=255)

    def __str__(self):
        return self.description

class Candidate(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    TITLE_CHOICES = [
        ('Mr.', 'Mr.'),
        ('Ms.', 'Ms.'),
        ('Dr.', 'Dr.'),
        ('Prof.', 'Prof.'),
    ]

    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True, null=True)  # Title with choices
    name = models.CharField(max_length=255)
    email = models.EmailField()
    member = models.ForeignKey('Position', on_delete=models.CASCADE, related_name='candidates')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    role = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='candidates')  

    def __str__(self):
        return self.name

class Role(models.Model):
    role_name = models.CharField(max_length=255)  
    role_level = models.IntegerField()  
    description = models.TextField(blank=True, null=True)  
    notes = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.role_name

class Committee(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255) 

    def __str__(self):
        return self.username