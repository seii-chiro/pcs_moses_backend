from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer, CustomUserUpdateSerializer

# Create your views here.


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        data = request.data

        # Check if they're trying to change sensitive info
        is_updating_sensitive = 'username' in data or 'new_password' in data

        if is_updating_sensitive:
            current_password = data.get('current_password')

            if not current_password or not user.check_password(current_password):
                return Response(
                    {'error': 'Current password is incorrect.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password if provided
            new_password = data.get('new_password')
            if new_password:
                user.set_password(new_password)

        # Proceed with serializer update
        serializer = CustomUserUpdateSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(CustomUserSerializer(user).data)
