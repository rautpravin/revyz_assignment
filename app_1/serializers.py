from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers

from app_1.models import (
    User, Country, State, City, Address, WorkExperience, TechSkill, Candidate, CandidateTechSkill,
    CandidateWorkExperience, JobLocationPreference
)
from app_1.utils import render_to_pdf


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'name', 'state')


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = '__all__'


class JobLocationPreferenceWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobLocationPreference
        fields = '__all__'


class JobLocationPreferenceReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobLocationPreference
        fields = ('id', 'candidate', 'city')
        depth = 1


class TechSkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = TechSkill
        fields = ('id', 'skill', )


class WorkExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkExperience
        fields = ('id', 'employer', 'joining_date', 'leaving_date', 'is_currently_working', )


class CandidateWorkExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateWorkExperience
        fields = '__all__'


class CandidateTechSkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateTechSkill
        fields = '__all__'


class CandidateWriteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    address = AddressSerializer()
    tech_skills = serializers.ListField(max_length=200)
    job_location_preferences = serializers.ListField(max_length=200)
    work_experiences = WorkExperienceSerializer(many=True)

    class Meta:
        model = Candidate
        fields = ('name', 'birth_date', 'gender', 'email', 'designation', 'contact_no_1', 'contact_no_2',
                  'address', 'user', 'tech_skills', 'job_location_preferences', 'work_experiences')

    def create(self, validated_data):
        print(validated_data.keys())
        tech_skills_data = validated_data.pop('tech_skills')
        tech_skill_ids = TechSkill.objects.filter(pk__in=tech_skills_data).values_list('id', flat=True)
        tech_skill_diff = set(tech_skills_data) - set(tech_skill_ids)

        if len(tech_skill_diff) != 0:
            raise serializers.ValidationError(f'invalid tech skill ids {tech_skill_ids}')

        job_loc_pref_data = validated_data.pop('job_location_preferences')
        city_ids = City.objects.filter(pk__in=job_loc_pref_data).values_list('id', flat=True)
        city_diff = set(job_loc_pref_data) - set(city_ids)
        if len(city_diff) != 0:
            raise serializers.ValidationError(f'invalid job_location_preferences ids {city_ids}')

        work_experiences_data = validated_data.pop('work_experiences')

        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)

        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)

        candidate = Candidate.objects.create(user=user, address=address, **validated_data)

        list_job_location_preferences = []
        for cid in city_ids:
            job_location_preference = JobLocationPreference.objects.create(candidate=candidate, city_id=cid)
            list_job_location_preferences.append(job_location_preference)

        list_candidate_tech_skills = []
        for tsi in tech_skill_ids:
            candidate_tech_skill = CandidateTechSkill.objects.create(candidate=candidate, tech_skill_id=tsi)
            list_candidate_tech_skills.append(candidate_tech_skill)

        list_work_experiences = []
        wes_ser = WorkExperienceSerializer(data=work_experiences_data, many=True)
        if wes_ser.is_valid(raise_exception=True):
            wes_recs = wes_ser.create(validated_data=wes_ser.validated_data)
            for wes_rec in wes_recs:
                candidate_work_experience = CandidateWorkExperience.objects.create(candidate=candidate, work_experience=wes_rec)
                list_work_experiences.append(candidate_work_experience)

        self.create_resume(candidate, list_work_experiences, list_candidate_tech_skills)
        return candidate

    def create_resume(self, candidate, work_experiences, tech_skills):
        f = render_to_pdf(
            'pdf/resume_format.html',
            filename=candidate.email,
            context_dict={
                'name': candidate.name,
                'designation': candidate.designation,
                'contact_no': candidate.contact_no_1,
                'email': candidate.email,
                'experiences': work_experiences,
                'skillsets': tech_skills,
                'dob': candidate.birth_date,
                'gender': candidate.gender,
            }
        )
        print('resume created: ', f)


class CandidateReadSerializer(serializers.ModelSerializer):

    tech_skills = serializers.SerializerMethodField()
    work_experiences = serializers.SerializerMethodField()
    job_location_preferences = serializers.SerializerMethodField()
    resume_link = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = ('id', 'name', 'email', 'contact_no_1', 'tech_skills', 'work_experiences',
                  'job_location_preferences', 'resume_link')

    def get_tech_skills(self, candidate):
        tc_ids = candidate.candidate_tech_skills.values_list('tech_skill_id', flat=True)
        ts = TechSkill.objects.filter(pk__in=tc_ids)
        return TechSkillSerializer(ts, many=True).data

    def get_work_experiences(self, candidate):
        wex_ids = candidate.candidate_work_experiences.values_list('work_experience_id', flat=True)
        wex = WorkExperience.objects.filter(pk__in=wex_ids)
        wex_data = WorkExperienceSerializer(wex, many=True).data
        return wex_data

    def get_job_location_preferences(self, candidate):
        city_ids = candidate.job_location_preferences.values_list('city_id', flat=True)
        cities = City.objects.filter(pk__in=city_ids)
        return CitySerializer(cities, many=True).data

    def get_resume_link(self, candidate):
        resume_url = str(settings.MEDIA_URL).replace('\\', '/')+f'{candidate.email}.pdf'
        return resume_url
