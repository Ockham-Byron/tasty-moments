from django.contrib import admin
from .models import *

# Register your models here.
class DishAdmin(admin.ModelAdmin):
  list_display=('name', 'created_at', 'updated_at')
  

admin.site.register(Dish, DishAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display=('dish', 'author', 'rating')

admin.site.register(Comment, CommentAdmin)

class MealAdmin(admin.ModelAdmin):
    list_display=('eaten_at',)

admin.site.register(Meal, MealAdmin)

admin.site.register(Music)
admin.site.register(Anecdote)
