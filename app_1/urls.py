from django.urls import path
from rest_framework import routers

from app_1 import viewsets
from app_1.viewsets import CustomAuthToken

router = routers.SimpleRouter(trailing_slash=True)
router.register(r'country', viewsets.CountyViewSet, basename='app_1')
router.register(r'state', viewsets.StateViewSet, basename='app_1')
router.register(r'city', viewsets.CityViewSet, basename='app_1')
router.register(r'candidate', viewsets.CandidateViewSet, basename='app_1')
router.register(r'job-loc-pref', viewsets.JobLocationPreferencesViewSet, basename='app_1')
router.register(r'tech-skill', viewsets.TechSkillViewSet, basename='app_1')
router.register(r'candidate-tech-skill', viewsets.CandidateViewSet, basename='app_1')

urlpatterns = [
    path(r'gettoken', CustomAuthToken.as_view()),
]

urlpatterns += router.urls
