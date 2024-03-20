# Generated by Django 5.0.3 on 2024-03-20 14:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('groups', '0002_initial'),
        ('meals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dish',
            name='chef',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dish',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dishes', to='groups.customgroup'),
        ),
        migrations.AddField(
            model_name='comment',
            name='dish',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dish_comments', to='meals.dish'),
        ),
        migrations.AddField(
            model_name='meal',
            name='dishes',
            field=models.ManyToManyField(blank=True, related_name='meals', to='meals.dish'),
        ),
        migrations.AddField(
            model_name='meal',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='groups.customgroup'),
        ),
        migrations.AddField(
            model_name='meal',
            name='guests',
            field=models.ManyToManyField(blank=True, related_name='guest_meals', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='anecdote',
            name='meal',
            field=models.ManyToManyField(blank=True, related_name='meal_anecdotes', to='meals.meal'),
        ),
        migrations.AddField(
            model_name='music',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_musics', to='groups.customgroup'),
        ),
        migrations.AddField(
            model_name='music',
            name='meal',
            field=models.ManyToManyField(blank=True, related_name='meal_musics', to='meals.meal'),
        ),
    ]