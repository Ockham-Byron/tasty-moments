from django import template
from meals.models import Comment

register = template.Library()

@register .simple_tag
def has_commented(dish):
    return Comment.objects.filter(dish=dish, author=request.user).exists()
