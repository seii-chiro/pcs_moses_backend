from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from .models import Election, Position, Candidate, Role
from .serializers import ElectionSerializer, PositionSerializer, CandidateSerializer, RoleSerializer, CommitteeSerializer

class ElectionListAPIView(generics.ListAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    permission_classes = [AllowAny]

class ElectionInitializeAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        election = Election.objects.first()
        if election:
            serializer = ElectionSerializer(election)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)

    def post(self, request):
        organization = request.data.get('organization')
        election_name = request.data.get('election_name')

        if Election.objects.filter(organization=organization, election_name=election_name).exists():
            return Response({"error": "An election with the same organization and election name already exists."}, 
                status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ElectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def put(self, request):
        election = Election.objects.first()
        if not election:
            return Response({"error": "No election found to update."}, status=status.HTTP_404_NOT_FOUND)

        # Get data from request
        organization = request.data.get('organization')
        election_name = request.data.get('election_name')
        voting_start = request.data.get('voting_start')
        voting_end = request.data.get('voting_end')
        poll_open_at = request.data.get('poll_open_at')
        poll_closed_at = request.data.get('poll_closed_at')
        no_slots = request.data.get('no_slots')
        no_ballots = request.data.get('no_ballots')

        # Update election instance
        election.organization = organization
        election.election_name = election_name
        election.voting_start = voting_start
        election.voting_end = voting_end
        election.poll_open_at = poll_open_at
        election.poll_closed_at = poll_closed_at
        election.no_slots = no_slots
        election.no_ballots = no_ballots

        election.save()

        serializer = ElectionSerializer(election)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ElectionCreateAPIView(generics.CreateAPIView):
    queryset = Election.objects.all()
    serializer_class = ElectionSerializer
    permission_classes = [AllowAny]

class ElectionRetrieveAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        try:
            if pk:  
                election = Election.objects.get(pk=pk)
            else:  
                election = Election.objects.first()

            if not election:
                return Response({"error": "No election found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = ElectionSerializer(election)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Election.DoesNotExist:
            return Response({"error": "Election not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ElectionUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            election = Election.objects.get(pk=pk)
            serializer = ElectionSerializer(election, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Election.DoesNotExist:
            return Response({"error": "Election not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ElectionDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, pk):
        try:
            election = Election.objects.get(pk=pk)
            election.delete()
            return Response({"message": "Election deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Election.DoesNotExist:
            return Response({"error": "Election not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Position Views
class PositionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [AllowAny]

class PositionRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [AllowAny]

class CandidateListCreateAPIView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]

class CandidateRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]

class RoleListAPIView(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class CommitteeListAPIView(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]