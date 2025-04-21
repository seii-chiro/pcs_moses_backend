from django.contrib import admin
from .models import Vote

class VoteAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('id', 'voter_id', 'candidate_id', 'voted_at', 'proxy_for_voter_id', 'is_counted')
    search_fields = ('voter_id', 'candidate_id', 'proxy_for_voter_id')
    list_filter = ('is_counted', 'created_at')

admin.site.register(Vote, VoteAdmin)
