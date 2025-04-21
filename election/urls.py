from django.urls import path
from .views import (
    ElectionInitializeAPIView,
    ElectionRetrieveAPIView,
    ElectionUpdateAPIView,
    ElectionDeleteAPIView,
    ElectionListAPIView,
    PositionListCreateAPIView,
    PositionRetrieveUpdateDeleteAPIView,
    CandidateListCreateAPIView,
    CandidateRetrieveUpdateDeleteAPIView,
    RoleListAPIView,
    CommitteeListAPIView,
)

urlpatterns = [
    # Election endpoints
    path('initialize/', ElectionInitializeAPIView.as_view(), name='initialize-election'),
    path('initialize/list/', ElectionListAPIView.as_view(), name='list-elections'),
    path('<int:pk>/', ElectionRetrieveAPIView.as_view(), name='retrieve-election'),
    path('<int:pk>/update/', ElectionUpdateAPIView.as_view(), name='update-election'),
    path('<int:pk>/delete/', ElectionDeleteAPIView.as_view(), name='delete-election'),

    path('positions/', PositionListCreateAPIView.as_view(), name='position-list-create'),
    path('positions/<int:pk>/', PositionRetrieveUpdateDeleteAPIView.as_view(), name='position-retrieve-update-delete'),

    # Candidate endpoints
    path('candidates/', CandidateListCreateAPIView.as_view(), name='candidate-list-create'),
    path('candidates/<int:pk>/', CandidateRetrieveUpdateDeleteAPIView.as_view(), name='candidate-retrieve-update-delete'),

    path('roles/', RoleListAPIView.as_view(), name='role-list'),

    path('committees/', CommitteeListAPIView.as_view(), name='committee-list'),
]