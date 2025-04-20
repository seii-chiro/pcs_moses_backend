from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer, CustomUserUpdateSerializer
from rest_framework import status
from .models import CustomUser
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
import pytz

# Create your views here.


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        data = request.data

        # Proceed with serializer update
        serializer = CustomUserUpdateSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(CustomUserSerializer(user).data)


@api_view(['GET'])
def get_all_voters(request):
    # Filter users who have the 'voter' role
    voters = CustomUser.objects.filter(role__id__in=[3, 4, 5, 6])
    serializer = CustomUserSerializer(
        voters, many=True)  # Serialize filtered users
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_proxy(request):
    user = request.user  # The requester
    proxy_id = request.data.get('proxy_id')
    reason = request.data.get('reason')
    try:
        proxy_user = CustomUser.objects.get(id=proxy_id)  # The proxy user
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if len(user.requested_proxy) >= 1:
        return Response({"error": "You can only request up to 1 proxy."}, status=status.HTTP_400_BAD_REQUEST)

    if any(req['user_id'] == proxy_id for req in user.requested_proxy):
        return Response({"error": "Proxy already requested."}, status=status.HTTP_400_BAD_REQUEST)

    current_datetime = datetime.now(pytz.UTC).isoformat()

    # Add to requester's requested_proxy list
    user.requested_proxy.append({
        "user_id": proxy_user.id,
        "first_name": proxy_user.first_name,
        "middle_name": proxy_user.middle_name,
        "last_name": proxy_user.last_name,
        "status": "pending",
        "date_assigned": current_datetime,
        "reason": reason
    })
    user.save()

    # Add to proxy user's received_proxy_requests list
    proxy_user.received_proxy_requests.append({
        "user_id": user.id,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "status": "pending",
        "date_assigned": current_datetime,
        "reason": reason
    })
    proxy_user.save()

    return Response({"message": "Proxy request sent."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def accept_proxy(request):
    user = request.user
    requester_id = request.data.get('requester_id')
    reason = request.data.get('reason')  # Get the reason (optional)

    try:
        requester = CustomUser.objects.get(id=requester_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "Requester not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check how many accepted proxies the requester already has
    accepted = [
        r for r in requester.requested_proxy if r['status'] == 'accepted']
    if len(accepted) >= 1:
        return Response({"error": "Requester already has an accepted proxy."}, status=status.HTTP_400_BAD_REQUEST)

    updated_requester = False
    updated_user = False

    # Update the requester's record
    for req in requester.requested_proxy:
        if req['user_id'] == user.id and req['status'] == 'pending':
            req['status'] = 'accepted'
            updated_requester = True
            if reason:
                requester.reason = reason
            break

    # Update the proxy user's record
    for req in user.received_proxy_requests:
        if req['user_id'] == requester.id and req['status'] == 'pending':
            req['status'] = 'accepted'
            updated_user = True
            break

    if not (updated_requester and updated_user):
        return Response({"error": "No matching pending request found."}, status=status.HTTP_400_BAD_REQUEST)

    requester.save()
    user.save()

    # If requester now has 1 accepted proxy, lock further requests
    if len([r for r in requester.requested_proxy if r['status'] == 'accepted']) == 1:
        requester.allow_proxy = False
        requester.save()

    return Response({"message": "Proxy request accepted."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reject_proxy(request):
    user = request.user  # The proxy user
    requester_id = request.data.get('requester_id')

    try:
        requester = CustomUser.objects.get(id=requester_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "Requester not found."}, status=status.HTTP_404_NOT_FOUND)

    original_len_requester = len(requester.requested_proxy)
    original_len_user = len(user.received_proxy_requests)

    # Remove from requester's list
    requester.requested_proxy = [
        r for r in requester.requested_proxy
        if not (r['user_id'] == user.id and r['status'] == 'pending')
    ]

    # Remove from proxy's (user's) list
    user.received_proxy_requests = [
        r for r in user.received_proxy_requests
        if not (r['user_id'] == requester.id and r['status'] == 'pending')
    ]

    if len(requester.requested_proxy) == original_len_requester and len(user.received_proxy_requests) == original_len_user:
        return Response({"error": "No pending request found to reject."}, status=status.HTTP_400_BAD_REQUEST)

    requester.save()
    user.save()

    return Response({"message": "Proxy request rejected."}, status=status.HTTP_200_OK)
