from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# verify enforcement of unique user email

# one to one relationship with User
class Profile(models.Model):
    description = models.CharField(max_length=1000)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    #profile_picture = models.ForeignKey(Photo, default=None)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class FriendGroup(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="groupowner")
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
