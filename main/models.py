import time

from django.contrib.auth.models import AbstractUser, User
from django.db import models


class Note(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    title = models.CharField(max_length=2048)
    photo = models.CharField(max_length=4096, null=True)
    date = models.DateField()
    text = models.TextField()
    watering_period = models.IntegerField(blank=True, null=True)  # in days
    fertilize_period = models.IntegerField(blank=True, null=True)  # in days

    def __str__(self):
        return self.title


class Bookmark(models.Model):
    id = models.IntegerField(auto_created=True, primary_key=True)
    user = models.ManyToManyField(User, related_name='bookmarks')
    note = models.TextField()
    last_watering = models.DateField(blank=True, null=True)
    last_fertilize = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'{self.note} ({self.last_watering})'


class Code(models.Model):
    id = models.IntegerField(auto_created=True, primary_key=True)
    code = models.CharField(max_length=6)
    user = models.ManyToManyField(User, related_name='code')

    def timer(self):
        time.sleep(60 * 5)
        self.delete()


class SiteStatistics(models.Model):
    id = models.IntegerField(auto_created=True, primary_key=True)
    last_login = models.DateField()
