# use this instead of the default hashing method
#from passlib.hash import pbkdf2_sha256

from django.db import models
from location_field.models.plain import PlainLocationField
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

#Documentation is a headache for me :3
# Create your models here.
class User(AbstractUser):
    '''
user model that's Inheriting from AbstractUser which is a django Built-in
User model, it's very handy because it takes care of storing/hashing passwords
and Authenticating users.
    '''
    first_name = models.CharField(max_length=60) #it's      obvious
    last_name = models.CharField(max_length=60)  #    Pretty       :3
    birthday = models.DateField() #obvious too :3
    biography = models.TextField(null=True, blank=True) # data isn't required
    avatar = models.ImageField(upload_to='media', default="media/no-avatar.jpg") # data isn't required
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    '''
    the below is the required Authentication field by AbstractUser, its value is
    the EmailField Cuz I choose it to force the user to authentuicate using it.
    the password is Handled Automatically by the module.
    '''
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    '''the required fields obviously is the additional fields that will be
       also stored with Email and password'''

    REQUIRED_FIELDS = ['first_name', 'last_name', 'birthday', 'gender', 'email']
    privateAccount = models.BooleanField(default=False)
    '''
    this method is responsible for making the account private.
    '''
    def setAccountToBePrivate(self):
        self.privateAccount = True
    '''
    this method is responsible for making the account public.
    '''
    def setAccoutToBePublic(self):
        self.privateAccount = False


class Comment(models.Model):
    user = models.ForeignKey(User) # ForeignKey to the user
    comment = models.TextField(max_length=2200) # comment data is required
    '''the params below is needed to force django to populate
       the field with current date on everytime data is saved to this model.'''
    created = models.DateTimeField(auto_now_add=True) # add current date.
    updated = models.DateTimeField(auto_now=True) # update date.

#this model is for storing posts as you can see :3
class Post(models.Model):
    user = models.ForeignKey(User, related_name='user') #ForeignKey to user
    '''important note: the params below is needed to force django to populate
       the field with current date on everytime data is saved to this model.'''
    created = models.DateTimeField(auto_now_add=True) # add current date.
    updated = models.DateTimeField(auto_now=True) # update date.
    '''params below is denoting that this field is Optional and django can
       put empty data in it'''
    description = models.TextField(max_length=2200,null=True, blank=True) # data isn't required
    '''tagging users, I think there's a logical error here.
     it will be changed soon to tag people on photos instead.
     also it isn't required.
     '''
    tag_user = models.ForeignKey(User, related_name='tag_user',null=True, blank=True)
    '''adding address for the location_field, it needs improvements IMO.'''
    address = models.CharField(max_length=255, null=True, blank=True)
    '''PlainLocationField is a field Inherited from location_field Lib.
       though its javascript is having errors! no data is required'''
    location = PlainLocationField(based_fields=['address'], zoom=7,null=True, blank=True)
    image = models.ImageField(upload_to='media') #fixed an issue in media directory
    # ForeignKey to the comment, though it's not required
    comments = models.ForeignKey(Comment,null=True, blank=True)

class Follow(models.Model):
    '''many to many relationship back into (User model) follow model'''
    follower = models.ForeignKey(User, related_name="Follower")
    followDate = models.DateField(auto_now=True)
    followed = models.ForeignKey(User, related_name="Followed")

class TimelineItem(models.Model):
    '''
    A model that make a timeline item for each post, it have many to many user
    relationship. and have a ForeignKey to the post.
    every instance of this TimelineItem model will be handled by a view when
    a user request the home page.
    '''
    followers = models.ManyToManyField(User, related_name="Followers")
    Date = models.DateField(auto_now=True)
    post = models.ForeignKey(Post, related_name="Post")

def create_TimelineItem(sender, **kwargs):
    '''
    A signal (hook) function to create Timeline Item.
    '''
    followers = [i.follower for i in Follow.objects.filter(followed=kwargs['instance'].user)]
    if kwargs['created']:
        timeline_item= TimelineItem.objects.create(post=kwargs['instance'])
        timeline_item.followers.add(kwargs['instance'].user,*followers)

# post_save signal connection between Post instance and create_TimelineItem function
post_save.connect(create_TimelineItem, sender=Post)
