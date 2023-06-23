from django.db.models.signals import post_save
from django.dispatch import receiver

from app_1.models import Candidate, WorkExperience, TechSkill
from app_1.utils import render_to_pdf


@receiver(post_save, sender=Candidate)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        pass
