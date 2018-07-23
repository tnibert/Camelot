from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from os import unlink
from .constants import *


# verify enforcement of unique user email

# one to one relationship with User
class Profile(models.Model):
    description = models.CharField(max_length=1000, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    profile_pic = models.ForeignKey('Photo', default=None, on_delete=models.SET_DEFAULT, null=True, blank=True)
    # display name
    dname = models.CharField(max_length=MAXDISPLAYNAME, default="")

    def __str__(self):
        """
        This will now be how we manage the distinction between displayname and username
        :return: display name or user name is no display name
        """
        if len(self.dname) == 0:
            return self.user.username
        else:
            return self.dname


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, dname=instance.username)
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

    def __str__(self):
        return str(self.name)


class Album(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=300)
    pub_date = models.DateTimeField('date published')
    contributors = models.ManyToManyField(Profile, related_name="albumcontributors")
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # 1 is public, 2 is all friends, 3 is groups, 4 is private
    accesstype = models.IntegerField(default=ALBUM_ALLFRIENDS)
    # we'll need to check that these are only groups owned by our contributors
    groups = models.ManyToManyField(FriendGroup, related_name="albumgroup")

    def __str__(self):
        return self.name


class Photo(models.Model):
    filename = models.CharField(max_length=200, default='')
    thumb = models.CharField(max_length=200, null=False)
    midsize = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=150)      # these length values should be defined elsewhere
    # foreign key - album
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    # set default on delete may not be appropriate
    # todo: be aware of this when we implement user deletion
    uploader = models.ForeignKey(Profile, default=None, on_delete=models.SET_DEFAULT, null=True, blank=True)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    # image mime type for full size image (mid and thumbs are png)
    imgtype = models.CharField(max_length=50, null=False)
    exiforientation = models.IntegerField(default=None, null=True, blank=True)


# receiver to delete the file on disk when we delete a photo from database
@receiver(post_delete, sender=Photo)
def delete_photo_file(sender, instance, *args, **kwargs):
    try:
        unlink(instance.filename)
    except FileNotFoundError:
        # todo: log
        pass
    try:
        unlink(instance.thumb)
    except FileNotFoundError:
        # todo: log
        pass
    try:
        unlink(instance.midsize)
    except FileNotFoundError:
        # todo: log
        pass
