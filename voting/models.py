from django.db import models

# Create your models here.
class Vote(models.Model):
    voted_at = models.DateTimeField(null=True, blank=True)
    voter_id = models.IntegerField(default=0)
    proxy_for_voter_id = models.IntegerField(default=0,  null=True, blank=True)
    candidate_id = models.IntegerField(default=0)
    notes = models.TextField(default='', blank=True)
    is_counted = models.BooleanField(default=False)
    counted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    # skip rec status
    #record_status = models.ForeignKey(RecordStatus, on_delete=models.PROTECT, default=1)

    def __str__(self):
        return f"Vote #{self.id} by Voter {self.voter_id}"
