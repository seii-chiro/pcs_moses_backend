from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Vote
from .serializers import VoteSerializer
from users.models import CustomUser  # Adjust if needed

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vote(request):
    try:
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            voter_id = serializer.validated_data['voter_id']
            candidate_ids = serializer.validated_data['candidate_id']  # Now a list
            notes = serializer.validated_data.get('notes', '')
            voted_at = serializer.validated_data.get('voted_at')

            if not isinstance(candidate_ids, list):
                return Response({"error": "candidate_id must be a list of candidate IDs."},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                voter = CustomUser.objects.get(id=voter_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "Voter not found."}, status=status.HTTP_404_NOT_FOUND)

            # Count total votes already cast by this voter
            total_votes = Vote.objects.filter(voter_id=voter_id).count()
            if total_votes >= 10:
                return Response(
                    {"error": "This voter has already cast the maximum number of votes (10)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if total_votes + len(candidate_ids) > 10:
                return Response(
                    {"error": f"You can only vote {10 - total_votes} more time(s)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if voter already voted for any of the selected candidates
            existing_votes = Vote.objects.filter(
                voter_id=voter_id, candidate_id__in=candidate_ids
            ).values_list('candidate_id', flat=True)

            if existing_votes:
                return Response(
                    {"error": f"You have already voted for candidate(s): {list(existing_votes)}"},
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
                proxy_for_voter_id = None

            # Create all votes
            votes = []
            for cid in candidate_ids:
                votes.append(Vote(
                    voter_id=voter_id,
                    proxy_for_voter_id=proxy_for_voter_id,
                    candidate_id=cid,
                    notes=notes,
                    voted_at=voted_at,
                    created_by=user.username,
                    updated_by=user.username,
                ))
            Vote.objects.bulk_create(votes)

            return Response({"message": f"Votes created for {len(candidate_ids)} candidate(s)."},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
