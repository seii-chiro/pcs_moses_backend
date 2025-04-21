from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Vote
from .serializers import VoteSerializer
from users.models import CustomUser  # Replace with your actual user import

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vote(request):
    try:
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            voter_id = serializer.validated_data['voter_id']
            candidate_id = serializer.validated_data['candidate_id']
            notes = serializer.validated_data.get('notes', '')
            voted_at = serializer.validated_data.get('voted_at')

            try:
                voter = CustomUser.objects.get(id=voter_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "Voter not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if vote already exists for the voter
            if Vote.objects.filter(voter_id=voter_id).exists():
                return Response(
                    {"error": "This voter has already cast a vote."},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
                proxy_for_voter_id = None  # self-vote

            vote = Vote.objects.create(
                voter_id=voter_id,
                proxy_for_voter_id=proxy_for_voter_id,
                candidate_id=candidate_id,
                notes=notes,
                voted_at=voted_at,
                created_by=user.username,
                updated_by=user.username,
            )

            return Response({"message": "Vote created successfully.", "vote_id": vote.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
