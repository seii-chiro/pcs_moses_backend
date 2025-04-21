from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from election.models import Election
from users.serializers import CustomUserSerializer
from .models import Vote
from .serializers import VoteSerializer
from users.models import CustomUser
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vote(request):
    try:
        # Check if there's an election
        election = Election.objects.first()
        if not election:
            return Response(
                {"error": "No election found. Please contact the election committee."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if the election is open
        now = timezone.now()
        if not (election.poll_open_at and election.poll_closed_at and election.poll_open_at <= now < election.poll_closed_at):
            return Response(
                {"error": "Voting is currently closed. Please check the election schedule."},
                status=status.HTTP_403_FORBIDDEN
            )

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

        # Extract existing request IDs
        existing_request_ids = {item.get('id') for item in proxy_requests if 'id' in item}

        # Extract incoming IDs
        incoming_ids = {item.get('id') for item in voter_data if 'id' in item}

        # Validate all incoming IDs exist in received_proxy_requests
        if not incoming_ids.issubset(existing_request_ids):
            return Response(
                {"error": "One or more voter IDs are not found in your received proxy requests."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check proxy limit
        current_proxy_count = CustomUser.objects.filter(proxy_id=user.id).count()
        if current_proxy_count + len(incoming_ids) > 2:
            return Response(
                {"error": f"You can only be assigned as a proxy for up to 2 users. Currently assigned: {current_proxy_count}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_voters = []

        for item in voter_data:
            voter_id = item.get('id')
            if not voter_id:
                continue

            try:
                requested_user = CustomUser.objects.get(id=voter_id)
            except CustomUser.DoesNotExist:
                return Response({"error": f"Voter with ID {voter_id} not found."}, status=status.HTTP_404_NOT_FOUND)

            # Accept proxy
            requested_user.allow_proxy = True
            requested_user.proxy_id = user.id
            requested_user.save()
            updated_voters.append(voter_id)

            # Update or append in received_proxy_requests
            updated = False
            for req in proxy_requests:
                if req.get("id") == voter_id:
                    req["status"] = "accepted"
                    req["date_accepted"] = now().isoformat()
                    updated = True
                    break

            if not updated:
                proxy_requests.append({
                    "id": voter_id,
                    "status": "accepted",
                    "date_accepted": now().isoformat()
                })

        user.received_proxy_requests = proxy_requests
        user.save()

        return Response({"message": "Proxy request(s) accepted and updated.", "updated_voter_ids": updated_voters}, status=status.HTTP_200_OK)

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_proxy_access(request):
    try:
        data = request.data

        if not isinstance(data, dict):
            return Response(
                {"error": "Request body must be a dictionary with 'proxy_id' and 'reason'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        proxy_id = data.get('proxy_id')
        reason = data.get('reason', '')

        if not isinstance(proxy_id, int):
            return Response(
                {"error": "'proxy_id' must be an integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        current_datetime = now().isoformat()

        try:
            proxy_user = CustomUser.objects.get(id=proxy_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": f"User with ID {proxy_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Build the request payload
        request_payload = {
            "id": user.id,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "status": "pending",
            "date_assigned": current_datetime,
            "reason": reason
        }

        current_requests = proxy_user.received_proxy_requests or []

        # Prevent duplicate requests
        if any(req.get("id") == user.id for req in current_requests):
            return Response(
                {"error": "You have already sent a proxy request to this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        current_requests.append(request_payload)
        proxy_user.received_proxy_requests = current_requests
        proxy_user.save()

        return Response(
            {"message": f"Proxy request sent to user ID {proxy_id}."},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
