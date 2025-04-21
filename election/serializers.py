from rest_framework import serializers
from .models import Election, Position, Candidate, Role, Committee
from datetime import datetime
from django.utils.timezone import make_aware, is_naive, now as timezone_now

class ElectionSerializer(serializers.ModelSerializer):
    is_open = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Election
        fields = '__all__'
        read_only_fields = ['is_open']

    def get_is_open(self, obj):
        now = timezone_now()

        voting_start = obj.voting_start
        voting_end = obj.voting_end

        if isinstance(voting_start, str):
            try:
                voting_start = datetime.strptime(voting_start, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return False

        if isinstance(voting_end, str):
            try:
                voting_end = datetime.strptime(voting_end, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return False

        if is_naive(voting_start):
            voting_start = make_aware(voting_start)
        if is_naive(voting_end):
            voting_end = make_aware(voting_end)

        return voting_start <= now < voting_end

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
