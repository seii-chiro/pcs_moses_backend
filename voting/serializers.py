from rest_framework import serializers
from .models import Vote

class VoteSerializer(serializers.ModelSerializer):
    candidate_id = serializers.IntegerField(required=True)
    voter_id = serializers.IntegerField(required=True)

    class Meta:
        model = Vote
        fields = [

            'candidate_id',
            'notes',
            'voted_at',
            'voter_id'
        ]
