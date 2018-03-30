from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .constants import *


# verify enforcement of unique user email

# one to one relationship with User
class Profile(models.Model):
    description = models.CharField(max_length=1000, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    #profile_picture = models.ForeignKey(Photo, default=None)
    # beware of this symmetrical thing, test well
    # ok, we've probably been overcomplicating this, friends are a one to many and we will access them through friendship
    #friends = models.Many #('self', through='Friendship', symmetrical=False)

    def __str__(self):
        return "Profile " + str(self.id) + ": " + str(self.user.username)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


# investigate constraints
# there should never be more than one of these for a given relationship
# including requester and requestee reversed
# so a Profile can have many Friendships
# there needs to be a better way, requester and requestee only matter until the friendship is confirmed
# after that, they should be the same
class Friendship(models.Model):
    class Meta:
        # define that requester and requestee must be a unique combination
        # check if this goes both ways interchangeably
        unique_together = ('requester', 'requestee')
    requester = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='requester')
    requestee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='requestee')
    confirmed = models.BooleanField(default=False)
    #created = models.DateTimeField('friends since')

    def __str__(self):
        return str(self.requester) + "->" + str(self.requestee) + " : " + str(self.confirmed)

class FriendGroup(models.Model):
    name = models.CharField(max_length=GROUPNAMELEN)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="groupowner")
    # may be better to link to Friendship, but maybe not
    members = models.ManyToManyField(Profile, related_name="groupmembers")

class Album(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=300)
    pub_date = models.DateTimeField('date published')
    contributors = models.ManyToManyField(Profile, related_name="albumcontributors")
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    # we'll need to check that these are only groups owned by our contributors
    groups = models.ManyToManyField(FriendGroup, related_name="albumgroup")

    def __str__(self):
        return self.name

class Photo(models.Model):
    filename = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=150)      # these length values should be defined elsewhere
    # foreign key - album
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    #uploader = models.ForeignKey(Profile, on_delete=models.CASCADE)
