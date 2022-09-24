from django.db import models

# Create your models here.
#class Teacher(models.Model):
 #   name = models.CharField(max_length=80)
  #  age = models.IntegerField()

#https://github.com/dead-claudia/github-limits
class GithubUser(models.Model):
    userName = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True) 
    websiteUrl = models.CharField(max_length=255, null=True)
    location =  models.CharField(max_length=255, null=True)  
    company = models.CharField(max_length=255, null=True) 
    bio = models.CharField(max_length=250, null=True) 
    avatarUrl = models.CharField(max_length=255, null=True)
    followersCount = models.IntegerField(default=0)
    repositoriesCount = models.IntegerField(default=0)
    forkCount = models.IntegerField(default=0)
    stargazerCount = models.IntegerField(default=0)
    mostUsedLanguage = models.CharField(max_length=150, null=True) 
