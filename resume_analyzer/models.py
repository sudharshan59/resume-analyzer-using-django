from django.db import models
from django.contrib import admin

class JobRole(models.Model):
    title = models.CharField(max_length=100, unique=True)
    keywords = models.JSONField(help_text="e.g., ['Python', 'Docker', 'CI/CD']")
    active = models.BooleanField(default=True)

class CompanyProfile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    keywords = models.JSONField()
    active = models.BooleanField(default=True)

class FeatureToggle(models.Model):
    name = models.CharField(max_length=50, unique=True)
    enabled = models.BooleanField(default=True)

@admin.register(JobRole, CompanyProfile, FeatureToggle)
class Admin(admin.ModelAdmin):
    pass