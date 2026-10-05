from django.db import models
from django.contrib.auth.models import User


class ResumeAnalysis(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    resume_name = models.CharField(
        max_length=255
    )

    resume_text = models.TextField()

    job_description = models.TextField(
        blank=True,
        default=""
    )

    score = models.IntegerField(
        default=0
    )

    category = models.CharField(
        max_length=100,
        default="General IT"
    )

    detected_skills = models.TextField(
        blank=True
    )

    job_skills = models.TextField(
        blank=True
    )

    matched_skills = models.TextField(
        blank=True
    )

    missing_skills = models.TextField(
        blank=True
    )

    match_percentage = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.resume_name