from rest_framework import serializers
from users.models import CustomUser as User
from django.contrib.auth.models import Group


class GroupSerializer(serializers.ModelSerializer):
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    class Meta:
        model = Group
        fields =  '__all__'
        ref_name = None


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    roles = serializers.StringRelatedField(source='groups', many=True, read_only=True)
    #personal_details = PersonalDetailsSerializer(source='personaldetails', read_only=True)
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    class Meta:
        model = User
        exclude = ['password']
        ref_name = None

    def get_groups(self, obj):
        groups = obj.groups.all()  # Access 'groups' directly on the User object
        group_serializer = GroupSerializer(groups, many=True)
        return group_serializer.data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
