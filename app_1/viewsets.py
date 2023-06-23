from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from app_1.models import (
    User, Country, State, City, Address, WorkExperience, TechSkill, Candidate, CandidateTechSkill,
    CandidateWorkExperience, JobLocationPreference
)
from app_1.serializers import (
    CountrySerializer, StateSerializer, CitySerializer, AddressSerializer, CandidateWriteSerializer,
    CandidateReadSerializer, JobLocationPreferenceWriteSerializer, JobLocationPreferenceReadSerializer,
    TechSkillSerializer, CandidateTechSkillSerializer, UserSerializer
)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token,created = Token.objects.get_or_create(user=user)
        return Response({
            'token':token.key,
            'user_id':user.pk,
            'email':user.email
        })


class CountyViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class StateViewSet(viewsets.ModelViewSet):
    serializer_class = StateSerializer
    queryset = State.objects.all()


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()

    def create(self, request, *args, **kwargs):
        city_ser = CitySerializer(data=request.data, many=True)
        if city_ser.is_valid(raise_exception=True):
            city_ser.create(city_ser.validated_data)
        return Response(data=city_ser.data, status=status.HTTP_201_CREATED)


class CandidateViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CandidateReadSerializer
        else:
            return CandidateWriteSerializer

    def get_queryset(self):
        city = self.request.query_params.get('city', None)
        tech_skill = self.request.query_params.get('tech_skill', None)
        candidate_ids_1 = []
        candidate_ids_2 = []

        if tech_skill:
            candidate_ids_1 = CandidateTechSkill.objects.filter(tech_skill__skill__icontains=tech_skill).values_list('candidate_id', flat=True)

        if city:
            candidate_ids_2 = JobLocationPreference.objects.filter(city__name=city).values_list('candidate_id', flat=True)

        if city and tech_skill:
            candidate_ids = set(candidate_ids_1).intersection(candidate_ids_2)
            queryset = Candidate.objects.filter(pk__in=candidate_ids)
            return queryset
        elif tech_skill:
            queryset = Candidate.objects.filter(pk__in=candidate_ids_1)
            return queryset
        elif city:
            queryset = Candidate.objects.filter(pk__in=candidate_ids_2)
            return queryset

        queryset = Candidate.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer_class()(data=request.data, many=True)
        if ser.is_valid(raise_exception=True):
            candidate_data = ser.create(ser.validated_data)
            return Response(data=CandidateReadSerializer(candidate_data, many=True).data, status=status.HTTP_201_CREATED)


class JobLocationPreferencesViewSet(viewsets.ModelViewSet):
    queryset = JobLocationPreference.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return JobLocationPreferenceReadSerializer
        return JobLocationPreferenceWriteSerializer


class TechSkillViewSet(viewsets.ModelViewSet):
    queryset = TechSkill.objects.all()

    def get_serializer_class(self):
       return TechSkillSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer_class()(data=request.data, many=True)
        if ser.is_valid(raise_exception=True):
            tech_skills = ser.create(validated_data=ser.validated_data)
            return Response(data=self.get_serializer_class()(tech_skills, many=True).data, status=status.HTTP_201_CREATED)


class CandidateTechSkillViewSet(viewsets.ModelViewSet):
    queryset = CandidateTechSkill.objects.all()

    def get_serializer_class(self):
       return CandidateTechSkillSerializer


