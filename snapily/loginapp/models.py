from django.db import models
from django.urls import reverse
from  django.contrib.auth.models import User , AbstractUser
from django.conf import settings

# Create your models here.


class Snapily(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=50) 
    photo = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

def __str__(self):
    return f'{self.user.username}-{self.text[:10]}'
    


#   <-----model for custum user-----> 

class CustemUser(AbstractUser):
    family_head = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='members')
    fullname = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=False)
    is_family_head = models.BooleanField(default=False)
    is_family_member = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, blank=True, null=True)
    relationship_to_admin = models.CharField(max_length=100, blank=True, null=True)
    admin_code = models.CharField(max_length=50, blank=True, null=True)
    member_id = models.CharField(max_length=50, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.username


# models for album creations 

class Album(models.Model):
    name = models.CharField(max_length=200)
    cover_photo = models.ImageField(upload_to="album_covers/")
    description = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="albums_created"
    )

    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="albums_shared"
    )

    share_family = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.created_by.username})"


class AlbumPhoto(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="album_photos/")
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo in {self.album.name}"

# model for memories --->

class Memory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memories")  
    image = models.ImageField(upload_to="memories/")  
    tag = models.CharField(max_length=100)  
    location = models.CharField(max_length=255, blank=True, null=True)  
    date = models.DateField(auto_now_add=True)  
    time = models.TimeField(auto_now_add=True)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.tag} - {self.user.username}"