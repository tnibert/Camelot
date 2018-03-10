from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# perhaps the way to handle plural is a one to many such as
# have a contributor model that just has foreign keys of profile
# and album...
# or, we could use postgres arrays?

# for the moment
# 1. register a user
# 2. create an album
# 3. upload images to that album
# will take care of friends after that

# one to one relationship with User
class Profile(models.Model):
    description = models.CharField(max_length=1000)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    #profile_picture = models.ImageField(upload_to='thumbpath', blank=True)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# we don't need this, use django user for auth and profile composed with user
#class AppUser(User):
    # friends
    # friendgroups
    # username = models.CharField(max_length=20)
    # password
    #profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

class Album(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=300)
    pub_date = models.DateTimeField('date published')
    # contributors
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # groups - we'll need to check that these are only groups owned by our contributors

    def __str__(self):
        return self.name

class Photo(models.Model):
    filename = models.CharField(max_length=200, default='')
    description = models.CharField(max_length=150)      # these length values should be defined elsewhere
    # foreign key - album
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    #uploader = models.ForeignKey(Profile, on_delete=models.CASCADE)
