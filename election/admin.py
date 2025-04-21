from django.contrib import admin
from .models import Election, Position, Candidate, Role, Committee

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'election_name', 'voting_start', 'no_slots', 'no_ballots', 'voting_end', 'is_poll_open', 'is_poll_closed', 'poll_open_at', 'poll_closed_at')
    search_fields = ('organization', 'election_name')
    list_filter = ('voting_start', 'voting_end')
    ordering = ('voting_start',)   

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('description', 'email', 'member')
    search_fields = ('description', 'email', 'member')
    list_filter = ('description',)
    ordering = ('description',)
    

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'get_member_name', 'get_gender_display', 'role', 'email')
    search_fields = ('name', 'member__description', 'gender', 'role__role_name', 'email')
    list_filter = ('member', 'gender', 'role')

    def get_member_name(self, obj):
        return obj.member.description 
    get_member_name.short_description = 'Member'

    def get_gender_display(self, obj):
        return obj.get_gender_display()  
    get_gender_display.short_description = 'Gender'

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'role_level', 'description', 'notes')
    search_fields = ('role_name', 'description')

@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'title', 'last_name')
    search_fields = ('username', 'email', 'full_name', 'title', 'last_name')
    list_filter = ('title',)
    ordering = ('username',)