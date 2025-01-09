from django.db import models

# Create your models here.

class User(models.Model):
    age = models.IntegerField()
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    
    def __str__(self):
        return self.name