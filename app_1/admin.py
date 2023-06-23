from django.contrib import admin

from app_1.models import *

admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Address)
admin.site.register(WorkExperience)
admin.site.register(CandidateWorkExperience)
admin.site.register(TechSkill)
admin.site.register(CandidateTechSkill)
admin.site.register(JobLocationPreference)
admin.site.register(Candidate)


