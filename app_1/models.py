from django.db import models
from django.contrib.auth.models import User


class LogModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class Country(LogModel):
    name = models.CharField('Name', max_length=60, unique=True, blank=False, null=False)


class State(LogModel):
    name = models.CharField('Name', max_length=60)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    class Meta:
        unique_together = ('country', 'name')


class City(LogModel):
    name = models.CharField('Name', max_length=60)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    class Meta:
        unique_together = ('state', 'name')


class Address(LogModel):
    address_line_1 = models.CharField(max_length=500, null=True, blank=True)
    address_line_2 = models.CharField(max_length=500, null=True, blank=True)
    landmark = models.CharField(max_length=200, null=True, blank=True)
    pincode = models.CharField(max_length=6)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='addresses')


class Candidate(LogModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='candidate')
    designation = models.CharField('Designation', max_length=100)
    name = models.CharField('Name', max_length=100)
    birth_date = models.DateField('Birth Date')
    gender = models.CharField('Gender', max_length=6, choices=(('Male', 'Male'), ('Female', 'Female')))
    email = models.EmailField('Email', max_length=255)
    contact_no_1 = models.CharField('Contact No 1', max_length=12)
    contact_no_2 = models.CharField('Contact No 2', max_length=12, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='candidates')


class WorkExperience(LogModel):
    employer = models.CharField('Employer', max_length=60)
    joining_date = models.DateField('Joining Date')
    leaving_date = models.DateField('Leaving Date', null=True, default=None)
    is_currently_working = models.BooleanField('Is Currently Working', default=True)


class CandidateWorkExperience(LogModel):
    work_experience = models.ForeignKey(WorkExperience, on_delete=models.CASCADE, related_name='candidate_work_experiences')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='candidate_work_experiences')


class TechSkill(LogModel):
    skill = models.CharField('Skill', max_length=100, unique=True, blank=False, null=False)

    def __str__(self):
        return f'{self.skill}'


class CandidateTechSkill(LogModel):
    tech_skill = models.ForeignKey(TechSkill, on_delete=models.CASCADE, related_name='candidate_tech_skills')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='candidate_tech_skills')

    class Meta:
        unique_together = ('tech_skill', 'candidate')


class JobLocationPreference(LogModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='job_location_preferences')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='job_location_preferences')

    class Meta:
        unique_together = ('candidate', 'city')

    def __str__(self):
        return f'{self.candidate.name} ({self.city.name}, {self.city.state.name})'
