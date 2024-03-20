from django.urls import path
from django.utils.translation import gettext as _
from .views import *



urlpatterns = [
    path(_('all-meals'), all_meals, name="all-meals"),
    path(_('group-meals/<slug>'), group_meals, name="group-meals"),
    path(_('add-meal'), add_meal, name="add-meal"),
    path(_('add-meal/<slug>'), add_meal_from_group, name="add-meal-from-group"),
    path(_('edit-meal/<slug>'), edit_meal, name="edit-meal"),
    path(_('delete-meal/<slug>'), delete_meal, name="delete-meal"),
    path(_('meal-detail-guest/<slug>/<guest>'),meal_detail_guest, name="meal-detail-guest"),

    #dishes
    path(_('all-dishes'), all_dishes, name="all-dishes"),
    path(_('group-dishes/<slug>'), group_dishes, name="group-dishes"),
    path(_('add-dish'), add_dish, name="add-dish"),
    path(_('add-dish-to-meal/<slug>'), add_dish_to_meal, name="add-dish-to-meal"),
    path(_('add-dish-to-group/<slug>'), add_dish_to_group, name="add-dish-to-group"),
    path(_('edit-dish/<slug>'), edit_dish, name="edit-dish"),
    path(_('delete-dish/<slug>'), delete_dish, name="delete-dish"),
    path(_('add-existing-dish/<slug>'), add_existing_dish_to_meal, name="add-existing-dish"),
    path(_('dish/<slug>'), dish_detail, name="dish-detail"),
    path(_('dish/<meal>/<dish>/<guest>'), dish_detail_with_guest, name="dish-detail-with-guest"),

    #comments
    path(_('add-comment/<slug>'), add_comment, name="add-comment"),
    path(_('add-comment/<meal>/<dish>/<guest>'), add_comment_guest, name="add-comment-guest"),
    path(_('edit-comment/<id>'), edit_comment, name="edit-comment"),
    path(_('edit-comment/<meal>/<dish>/<guest>/<id>'), edit_comment_guest, name="edit-comment-guest"),
    path(_('delete-comment/<id>'), delete_comment, name="delete-comment"),

    #musics
    path(_('add-music/<slug>'), add_music, name="add-music"),
    path(_('edit-music/<id>'), edit_music, name="edit-music"),
    path(_('delete-music/<id>'), delete_music, name="delete-music"),
    path(_('group-music/<slug>'), group_musics, name="group-musics"),

    #anecdotes
    path(_('anecdote/<slug>'), add_anecdote, name="add-anecdote"),
    path(_('edit-anecdote/<id>'), edit_anecdote, name="edit-anecdote"),
    path(_('delete-anecdote/<id>'), delete_anecdote, name="delete-anecdote"),
    path(_('group-anecdotes/<slug>'), group_anecdotes, name="group-anecdotes"),

    #guest
    path(_('invite-guest/<slug>'), invite_guest, name="invite-guest"),


]