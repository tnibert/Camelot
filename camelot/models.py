from django.db import models

# perhaps the way to handle plural is a one to many such as
# have a contributor model that just has foreign keys of user
# and album...
# or, we could use postgres arrays?

# one to one relationship with User    
class Profile(models.Model):
    description = models.CharField(max_length=1000)
    # albums

class User(models.Model):
    # friends
    # friendgroups
    username = models.CharField(max_length=20)
    # password
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

class Album(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=300)
    pub_date = models.DateTimeField('date published')
    # contributors
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # groups - we'll need to check that these are only groups owned by our contributors

    def __str__(self):
        return self.name

class Photo(models.Model):
    filename = models.CharField(max_length=200)
    # foreign key - album
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
