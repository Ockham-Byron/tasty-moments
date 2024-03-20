from uuid import uuid4
import os
from django.db.models import Avg, Count
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from PIL import Image
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from groups.models import CustomGroup

User=get_user_model()

#function to rename avatar file on upload
def path_and_rename(instance, filename):
    upload_to = 'recipes_pictures'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}-{}.{}'.format(instance.name, instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}-{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

def path_and_rename_meal(instance, filename):
    upload_to = 'meals_pictures'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}-{}.{}'.format(instance.created_at, instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}-{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


# Create your models here.
class Dish(models.Model):
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    name=models.CharField(max_length=100, blank=False, null=False)
    chef=models.ManyToManyField(User, blank=True)
    picture=models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, related_name="dishes")
    slug = models.SlugField(max_length=255, unique= True, default=None, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save()
        # create slug
        if not self.slug:
            self.slug = slugify(self.name + '_' + str(self.id))
        super(Dish, self).save(*args, **kwargs)

    def averagereview(self):
        if Comment.objects.filter(dish=self).exists():
            comments = Comment.objects.filter(dish=self).aggregate(average=Avg('rating'))
            avg=0
            if ["average"] is not None:
                avg=float(comments["average"])
            return avg
        

    def countreview(self):
        comments = Comment.objects.filter(product=self).aggregate(count=Count('id'))
        cnt=0
        if comments["count"] is not None:
            cnt = int(comments["count"])
        return cnt
    

class Comment(models.Model):
    dish=models.ForeignKey(Dish, related_name="dish_comments", on_delete=models.CASCADE)
    author=models.ForeignKey(User, related_name="user_comments", on_delete=models.CASCADE)
    rating=models.IntegerField(validators=[MaxValueValidator(10), MinValueValidator(0)], blank=False, null=False)
    message=models.CharField(max_length=500, blank=True, null=True)

class Meal(models.Model):
    id = models.UUIDField(default = uuid4, editable = False, primary_key=True)
    dishes=models.ManyToManyField(Dish, blank=True, related_name="meals")
    picture=models.ImageField(upload_to=path_and_rename_meal, blank=True, null=True)
    eaten_at=models.DateField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique= True, default=None, null=True)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, related_name="meals")
    guests = models.ManyToManyField(User, blank=True, related_name="guest_meals")

    def __str__(self):
        return str(self.created_at)

    def save(self, *args, **kwargs):
        super().save()
        # create slug
        if not self.slug:
            self.slug = slugify(str(self.created_at) + '_' + str(self.id))
        super(Meal, self).save(*args, **kwargs)

class Music(models.Model):
    meal=models.ManyToManyField(Meal, blank=True, related_name="meal_musics")
    title=models.CharField(max_length=100, blank=True, null=True)
    artist=models.CharField(max_length=100, blank=True, null=True)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, related_name="group_musics", null=True)

    def __str__(self):
        return self.title

class Anecdote(models.Model):
    meal=models.ManyToManyField(Meal, blank=True, related_name="meal_anecdotes")
    message=models.TextField(blank=False, null=False)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE, related_name="group_anecdotes", null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.message[:30]



    

    