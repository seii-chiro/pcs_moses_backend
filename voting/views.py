from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.serializers import CustomUserSerializer
from .models import Vote
from .serializers import VoteSerializer
from users.models import CustomUser

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vote(request):
    try:
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Check if user's role is not allowed to vote
            if user.role and user.role.role_name in ['Elecom', 'Administrator']:
                return Response(
                    {"error": f"The role '{user.role.role_name}' is not allowed to vote."},
                    status=status.HTTP_403_FORBIDDEN
                )

            voter_id = serializer.validated_data['voter_id']
            candidate_ids = serializer.validated_data['candidate_id']  # This should be a list
            notes = serializer.validated_data.get('notes', '')
            voted_at = serializer.validated_data.get('voted_at')

            try:
                voter = CustomUser.objects.get(id=voter_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "Voter not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check for proxy voting
            if voter_id != user.id:
                if not getattr(voter, 'allow_proxy', False):
                    return Response(
                        {"error": "This voter does not allow proxy voting."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                if voter.proxy_id != user.id:
                    return Response(
                        {"error": "You are not authorized to vote as proxy for this voter."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                proxy_for_voter_id = user.id
            else:
                proxy_for_voter_id = None

            # Check if voter already reached max allowed votes (10)
            vote_count = Vote.objects.filter(voter_id=voter_id).count()
            if vote_count + len(candidate_ids) > 10:
                return Response(
                    {"error": f"This voter can only vote 10 times in total. Already voted: {vote_count}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prevent voting for the same candidate more than once
            already_voted = Vote.objects.filter(voter_id=voter_id, candidate_id__in=candidate_ids).values_list('candidate_id', flat=True)
            duplicates = set(already_voted).intersection(candidate_ids)
            if duplicates:
                return Response(
                    {"error": f"This voter has already voted for candidate(s): {list(duplicates)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create votes
            created_votes = []
            for candidate_id in candidate_ids:
                vote = Vote.objects.create(
                    voter_id=voter_id,
                    proxy_for_voter_id=proxy_for_voter_id,
                    candidate_id=candidate_id,
                    notes=notes,
                    voted_at=voted_at,
                    created_by=user.username,
                    updated_by=user.username,
                )
                created_votes.append(vote.id)

            return Response(
                {"message": "Votes created successfully.", "vote_ids": created_votes},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_requested_proxy(request):
    try:
        voter_data = request.data

        if not isinstance(voter_data, list):
            return Response({"error": "Request body must be a list of voter ID objects."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        proxy_requests = user.received_proxy_requests or []

        # Extract requested voter IDs from received_proxy_requests
        requested_ids = {item['id'] for item in proxy_requests if 'id' in item}

        # Extract voter IDs from request
        incoming_ids = {item['id'] for item in voter_data if 'id' in item}

        # Validate all incoming IDs exist in received_proxy_requests
        if not incoming_ids.issubset(requested_ids):
            return Response(
                {"error": "One or more voter IDs are not found in your received proxy requests."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if assigning would exceed max of 2 proxy relationships
        current_proxy_count = CustomUser.objects.filter(proxy_id=user.id).count()
        if current_proxy_count + len(incoming_ids) > 2:
            return Response(
                {"error": f"You can only be assigned as a proxy for up to 2 users. Currently assigned: {current_proxy_count}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_voters = []

        for voter_id in incoming_ids:
            try:
                requested_user = CustomUser.objects.get(id=voter_id)
            except CustomUser.DoesNotExist:
                return Response({"error": f"Voter with ID {voter_id} not found."}, status=status.HTTP_404_NOT_FOUND)

            requested_user.allow_proxy = True
            requested_user.proxy_id = user.id
            requested_user.save()
            updated_voters.append(voter_id)

        return Response({"message": "Proxy request(s) accepted.", "updated_voter_ids": updated_voters}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_proxy_assignments(request):
    try:
        voter_data = request.data

        if not isinstance(voter_data, list):
            return Response({"error": "Request body must be a list of voter ID objects."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        incoming_ids = {item['id'] for item in voter_data if 'id' in item}

        updated_voters = []

        for voter_id in incoming_ids:
            try:
                voter = CustomUser.objects.get(id=voter_id)
            except CustomUser.DoesNotExist:
                continue  # Skip if not found

            # Only remove if the logged-in user is currently the proxy
            if voter.proxy_id == user.id:
                voter.allow_proxy = False
                voter.proxy_id = None
                voter.save()
                updated_voters.append(voter_id)

        return Response(
            {"message": "Proxy assignments removed.", "updated_voter_ids": updated_voters},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_proxied_users(request):
    try:
        user = request.user
        proxied_users = CustomUser.objects.filter(proxy_id=user.id)

        serializer = CustomUserSerializer(proxied_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
