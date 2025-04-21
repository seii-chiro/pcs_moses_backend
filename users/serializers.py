# users/serializers.py
from rest_framework import serializers

from voting.models import Vote
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    vote_status = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = CustomUser
        exclude = ['password', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_vote_status(self, obj):
        # Count votes cast directly by the user
        total_votes = Vote.objects.filter(voter_id=obj.id).count()

        # Count votes cast by this user on behalf of others (as a proxy)
        proxied_votes = Vote.objects.filter(proxy_for_voter_id=obj.id).count()

        return {
            "status": "Voted" if total_votes > 0 else "Not Voted",
            "total_votes": total_votes,
            "proxied_user_votes": proxied_votes
        }


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        exclude = ['date_joined', 'last_login']

    def to_internal_value(self, data):
        # includes declared + model fields
        allowed_fields = set(self.fields.keys())
        filtered = {key: value for key,
                    value in data.items() if key in allowed_fields}
        return super().to_internal_value(filtered)

    def validate(self, data):
        user = self.instance

        current = data.get("current_password")
        new = data.get("new_password")
        confirm = data.get("confirm_password")

        # Password update logic
        if current or new or confirm:  # Check if any of the password fields are present
            # Validate current password
            if not current or not user.check_password(current):
                raise serializers.ValidationError(
                    {"current_password": "Current password is incorrect."}
                )
            if new != confirm:  # Ensure new and confirm passwords match
                raise serializers.ValidationError(
                    {"confirm_password": "Passwords do not match."}
                )
            if new and len(new) < 8:  # Password length validation
                raise serializers.ValidationError(
                    {"new_password": "Password must be at least 8 characters long."}
                )

        return data

    def update(self, instance, validated_data):
        validated_data.pop("current_password", None)
        new_password = validated_data.pop("new_password", None)
        validated_data.pop("confirm_password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance
