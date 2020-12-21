from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=200)
    identifier = models.TextField()
    url = models.CharField(max_length=200)
    is_owner = models.BooleanField(default=False)
    is_followed = models.BooleanField(default=False)
    is_follower = models.BooleanField(default=False)
    # make sure we only save 1 entry for the Person. 
    # This represents the owner of the website
    def save(self, *args, **kwargs):
        count = Person.objects.count()
        if count <= 1:
            super().save(*args, **kwargs)
        else:
            raise Exception("Cannot save more than 1 entry for website owner")
            

class SubscriptionPerson(models.Model):
    name = models.CharField(max_length=200)
    identifier = models.TextField()
    url = models.CharField(max_length=200)
    is_followed = models.BooleanField(default=False)

class Post(models.Model):
    author = models.CharField(max_length=200)    
    video = models.CharField(max_length=200, null=True)
    text = models.TextField(null=True)          
    audio = models.CharField(max_length=200, null=True)          
    thumbnailURL = models.CharField(max_length=200, null=True)
    image = models.CharField(max_length=250, null=True)
    is_draft = models.BooleanField(default=True)
    date_saved = models.DateTimeField(auto_now_add=True, null=True)

class Message(models.Model):
    dateRead = models.DateTimeField(null=True)
    dateSent = models.DateTimeField(null=True)
    dateReceived = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey('Person', related_name='message_sent', on_delete=models.SET_NULL, null=True)
    receipent = models.ForeignKey('Person', related_name='messaged_received', on_delete=models.SET_NULL, null=True)
    messageAttachment = models.ForeignKey('Post', on_delete=models.SET_NULL, null=True)
