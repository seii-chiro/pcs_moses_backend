from rest_framework import serializers
from .models import Election, Position, Candidate, Role, Committee
from django.utils import timezone


class ElectionSerializer(serializers.ModelSerializer):
    is_open = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Election
        fields = '__all__'
        read_only_fields = ['is_open']

    def get_is_open(self, obj):
        now = timezone.now()
        return (
            obj.poll_open_at is not None and
            obj.poll_closed_at is not None and
            obj.poll_open_at <= now < obj.poll_closed_at
        )


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_name', 'role_level', 'description', 'notes']

class CandidateSerializer(serializers.ModelSerializer):
    member = serializers.CharField(source='member.description', read_only=True)  # Member description
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'title', 'name', 'gender', 'role', 'member']

class CommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Committee
        fields = ['username', 'email', 'full_name', 'title', 'last_name']
