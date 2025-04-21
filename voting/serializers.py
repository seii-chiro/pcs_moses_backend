from rest_framework import serializers

class VoteSerializer(serializers.Serializer):
    candidate_id = serializers.ListField(
        child=serializers.IntegerField(), required=True
    )
    voter_id = serializers.IntegerField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    voted_at = serializers.DateTimeField(required=False)

    # No Meta class needed since this isn't tied to a single Vote instance
