from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Count, Q
from .models import *
from .forms import *

    
def get_groups(user):
    groups = CustomGroup.objects.filter(members__id__contains=user.id)
    nb_of_groups = len(groups)
    if nb_of_groups == 0:
        group = None
    elif nb_of_groups >= 1:
        group = groups
        

    return group

# Create your views here.
@login_required
def add_dish(request):
    groups = get_groups(request.user)
    is_group = False
    no_meal = True
    if len(groups) == 1:
        is_group = True
        group = groups[0]
    if groups is None:
        return redirect('all-groups')
    
    if is_group:
        print("group unique")
        form = AddDishForm(group)
        if request.method == "POST":
            form=AddDishForm(group, request.POST, request.FILES)
            chefs = request.POST.getlist('chef')
            meal = request.POST.get('meal')
            meal = Meal.objects.get(id=meal)
            if form.is_valid():
                dish=form.save(commit=False)
                dish.group = group
                dish.save()
                if chefs:
                    for chef in chefs:
                        user = User.objects.get(id=chef)
                        dish.chef.add(user)
                dish.save()
                meal.dishes.add(dish)
                meal.save()
                
                return redirect('all-dishes')
    
        return render(request, "meals/add-dish.html", {'form':form, 'is_group':is_group, 'groups':groups, 'group':group, 'no_meal':no_meal})
    
    else:
        return render(request, "meals/choose-group.html")
    

   
@login_required
def add_dish_to_group(request, slug):
    group = CustomGroup.objects.get(slug=slug)
    form = AddDishForm(group)
    is_group = True
    no_meal = True

    if request.method == "POST":
        form=AddDishForm(group, request.POST, request.FILES)
        chefs = request.POST.getlist('chef')
        meal = request.POST.get('meal')
        meal = Meal.objects.get(id=meal)
        if form.is_valid():
            dish=form.save(commit=False)
            dish.group = group
            dish.save()
            if chefs:
                for chef in chefs:
                    user = User.objects.get(id=chef)
                    dish.chef.add(user)
            dish.save()
            meal.dishes.add(dish)
            meal.save()
            
            return redirect('all-dishes')
            
    return render(request, "meals/add-dish.html", {'form':form, 'is_group':is_group, 'group':group, 'no_meal':no_meal})
    
@login_required
def all_dishes(request):
    groups = get_groups(request.user)
    if groups is None:
        return redirect('all-groups')
    else:
        for group in groups:
            dishes = Dish.objects.filter(group__members__id__contains = request.user.id).distinct()
            dishes = dishes.annotate(
            has_commented=Count('dish_comments', filter=Q(dish_comments__author=request.user))
    )

        context={
            'dishes':dishes
        }
        return render(request, "meals/all-dishes.html", context=context)

@login_required
def group_dishes(request, slug):
    group = get_object_or_404(CustomGroup, slug=slug)
    dishes = Dish.objects.filter(group=group)

    context = {'dishes': dishes,
               'group': group}
    return render(request, 'meals/all-dishes.html', context=context)

@login_required
def dish_detail(request, slug):
    dish=get_object_or_404(Dish, slug=slug)
    comments=Comment.objects.filter(dish=dish)
    not_commented = True
    if Comment.objects.filter(dish=dish, author=request.user).exists():
        not_commented = False
    
    print(not_commented)

    context={
        'dish':dish,
        'comments':comments,
        'not_commented':not_commented
        
    }
    
    return render(request, "meals/dish-detail.html", context=context)

@login_required
def dish_detail_with_guest(request, meal, dish, guest):
    meal=get_object_or_404(Meal, slug=meal)
    dish=get_object_or_404(Dish, slug=dish)
    guest=get_object_or_404(User, slug=guest)

    comments=Comment.objects.filter(dish=dish)
    
    guestcomments = Comment.objects.filter(dish=dish, author=guest)

    print(guestcomments)
    
   
    
    

    context={
        'meal':meal,
        'dish':dish,
        'comments':comments,
        'guest':guest,
        'guestcomments':guestcomments,
        
    }
    
    return render(request, "meals/dish-detail.html", context=context)

@login_required
def edit_dish(request, slug):
    dish = get_object_or_404(Dish, slug=slug)
    group = dish.group
    is_group = True
    form=AddDishForm(group=group, instance=dish)

    if request.method == "POST":
        form = AddDishForm(group, request.POST, request.FILES, instance=dish)
        if form.is_valid() or is_group:
            dish.name=request.POST.get('name')
            dish.picture=request.FILES.get('picture')
            chefs = request.POST.getlist('chef')
            dish.chef.clear()
            if chefs:
                for chef in chefs:
                    user = User.objects.get(id=chef)
                    dish.chef.add(user)
            dish.save()
            return redirect('dish-detail', dish.slug)
        else:
            print(form.errors)

    return render(request, "meals/add-dish.html", {'form':form, 'is_group':is_group, 'dish':dish})

@login_required
def delete_dish(request, slug):
    dish = get_object_or_404(Dish, slug=slug)
    if dish.picture:
        os.remove(dish.picture.path)
        dish.picture.delete()
    dish.delete()
    return redirect('all-dishes')

@login_required
def add_comment(request, slug):
    dish=get_object_or_404(Dish, slug=slug)
    form=AddCommentForm()

    if request.method=='POST':
        form=AddCommentForm(request.POST)
        if form.is_valid():
            comment=form.save(commit=False)
            comment.dish=dish
            comment.author=request.user
            comment.save()
            return redirect('dish-detail', dish.slug)

    return render(request, "meals/add-comment.html", {'form':form, 'dish':dish})

@login_required
def add_comment_guest(request,meal, dish, guest):
    meal=get_object_or_404(Meal, slug=meal)
    dish=get_object_or_404(Dish, slug=dish)
    guest=get_object_or_404(User, slug=guest)
    form=AddCommentForm()

    if request.method=='POST':
        form=AddCommentForm(request.POST)
        if form.is_valid():
            comment=form.save(commit=False)
            comment.dish=dish
            comment.author=guest
            comment.save()
            return redirect('meal-detail-guest', meal.slug, guest.slug)

    return render(request, "meals/add-comment.html", {'form':form, 'dish':dish, 'guest':guest})


@login_required
def edit_comment(request,id):
    comment=get_object_or_404(Comment, id=id)
    dish=comment.dish
    form=AddCommentForm(instance=comment)
    if request.method=='POST':
        form=AddCommentForm(request.POST, instance=comment)
        comment=form.save()
        comment.save()
        return redirect('dish-detail', dish.slug)
    
    return render(request, "meals/add-comment.html", {'form':form, 'dish':dish, 'comment':comment})

@login_required
def edit_comment_guest(request,meal, dish, guest, id):
    meal=get_object_or_404(Meal, slug=meal)
    dish=get_object_or_404(Dish, slug=dish)
    guest=get_object_or_404(User, slug=guest)
    comment=get_object_or_404(Comment, id=id)
    dish=comment.dish
    form=AddCommentForm(instance=comment)
    if request.method=='POST':
        form=AddCommentForm(request.POST, instance=comment)
        comment=form.save()
        comment.save()
        return redirect('dish-detail-with-guest', meal.slug, dish.slug, guest.slug)
    
    return render(request, "meals/add-comment.html", {'form':form, 'dish':dish, 'comment':comment})

@login_required
def delete_comment(request,id):
    comment=get_object_or_404(Comment, id=id)
    dish=comment.dish
    comment.delete()
    return redirect('dish-detail', dish.slug)

@login_required
def add_meal(request):
    form=AddMealForm(request.user)
    group = get_groups(request.user)
    is_dish = False
    if Dish.objects.filter(group__in=group).exists():
        is_dish = True
    is_group = False
    if len(group) == 1:
                is_group = True
    if group is None:
        return redirect('all-groups')
    
    else:
        if request.method == "POST":
            print("request method is POST")
            form=AddMealForm(request.user, request.POST, request.FILES)
            if len(group) == 1:
                group = CustomGroup.objects.get(uuid=group[0].uuid)
                is_group = True
            else:
                group = request.POST.get('group')
                if group is not None:
                    print("y a un groupe")
                    group = CustomGroup.objects.get(uuid=group)
                else:
                    print("manque le groupe")

            if form.is_valid() or group is not None:
                print("ok")
                eaten_at = request.POST.get('eaten_at')
                picture = request.FILES.get('picture')
                dishes = request.POST.getlist('dishes')
                
                meal = Meal(eaten_at=eaten_at,picture=picture, group=group)
                meal.save()
                if dishes:
                    for i in dishes:
                        dish = Dish.objects.get(id=i)
                        meal.dishes.add(dish)
                    meal.save()
                    

                if 'add-dish' in request.POST:
                    return redirect('add-dish-to-meal', meal.slug)
                if 'add-existing-dish' in request.POST:
                    return redirect('add-existing-dish', meal.slug)
                if 'create-meal' in request.POST:
                    return redirect('all-meals')
            
            else:
                print("not ok")
                messages.error(request,_('Please select the group you shared the meal with.'))
                return redirect('add-meal')

        return render(request, "meals/add-meal.html", {'form':form, 'is_group':is_group, 'is_dish':is_dish})

@login_required
def add_meal_from_group(request, slug):
    form=AddMealForm(request.user)
    group = CustomGroup.objects.get(slug=slug)
    is_dish = False
    if Dish.objects.filter(group=group).exists():
        is_dish = True
    is_group = True

    if request.method == "POST":
        form=AddMealForm(request.user, request.POST, request.FILES)
        print(group)
        if form.is_valid() or is_group :
            eaten_at = request.POST.get('eaten_at')
            picture = request.FILES.get('picture')
            dishes = request.POST.get('dishes')
            if dishes is not None:
                meal = Meal(eaten_at=eaten_at,picture=picture,dishes=dishes.set(), group=group)
            else:
                meal = Meal(eaten_at=eaten_at,picture=picture, group=group)
            meal.save()
            if 'add-dish' in request.POST:
                return redirect('add-dish-to-meal', meal.slug)
            if 'add-existing-dish' in request.POST:
                return redirect('add-existing-dish', meal.slug)
            if 'create-meal' in request.POST:
                return redirect('all-meals')
            
        else:
            print(form.errors)

    return render(request, "meals/add-meal.html", {'form':form, 'is_group':is_group, 'is_dish':is_dish})

@login_required
def edit_meal(request, slug):
    meal = get_object_or_404(Meal, slug=slug)
    form = AddMealForm(request.user, instance = meal)
    is_group = True
    group = meal.group

    if request.method == 'POST':
        form = AddMealForm(request.user, request.POST, request.FILES, instance=meal)
        if form.is_valid() or is_group:
                eaten_at = request.POST.get('eaten_at')
                picture = request.FILES.get('picture')
                dishes = request.POST.getlist('dishes')
                
                # meal.dishes.through.objects.all().delete()
                
                meal.eaten_at = eaten_at
                meal.picture = picture
                meal.group = group
                meal.save()
                if dishes:
                    for i in dishes:
                        dish = Dish.objects.get(id=i)
                        if dish not in meal.dishes.all():
                            meal.dishes.add(dish)
                    meal.save()
                    

                if 'add-dish' in request.POST:
                    return redirect('add-dish-to-meal', meal.slug)
                if 'create-meal' in request.POST:
                    return redirect('all-meals')
            
        else:
            print(form.errors)
     

    return render(request, 'meals/add-meal.html', {'form': form, 'meal': meal, 'is_group': is_group})

@login_required
def delete_meal(request, slug):
    meal = get_object_or_404(Meal, slug=slug)
    if meal.picture:
        os.remove(meal.picture.path)
        meal.picture.delete()
    anecdotes = Anecdote.objects.filter(meal=meal)
    for anecdote in anecdotes:
        anecdote.delete()
    meal.delete()
    return redirect('all-meals')

@login_required
def add_dish_to_meal(request, slug):
    meal = get_object_or_404(Meal, slug=slug)
    group = meal.group
    is_group = True
    chefs = group.members.all().exclude(is_guest=True)
    guests = meal.guests.all().exclude(is_guest=False)
    chefs=chefs.union(guests)
    
    form=AddDishForm(group)

    if request.method == "POST":
        form=AddDishForm(group, request.POST, request.FILES)
        chefs = request.POST.getlist('chef')
        
        print(chefs)
        if form.is_valid():
            dish=form.save(commit=False)
            dish.group=group
            dish.save()
            if chefs:
                for chef in chefs:
                    user = User.objects.get(id=chef)
                    dish.chef.add(user)
            dish.save()
            meal.dishes.add(dish)
            meal.save()
            return redirect('all-meals')
        
    else:
        print("Nothing")

    return render(request, "meals/add-dish.html", {'form':form, 'is_group':is_group, 'meal':meal, 'chefs':chefs})

@login_required
def add_existing_dish_to_meal(request, slug):
    meal = get_object_or_404(Meal, slug=slug)
    
    
    dishes = Dish.objects.filter(group= meal.group).exclude(meals__id__contains = meal.id)
    

    if request.method == "POST":
        if 'create-dish' in request.POST:
            return redirect('add-dish-to-meal', meal.slug)
        if 'add-dish' in request.POST:
            dishes=request.POST.getlist('dish')
            for dish in dishes:
                dish = Dish.objects.get(id=dish)
                print(dish)
                meal.dishes.add(dish)
            meal.save()
            return redirect('all-meals')
        
    else:
        print("Nothing")

    if dishes:

        return render(request, "meals/add-existing-dish.html", {'meal':meal, 'dishes':dishes})

    else:
        return redirect('add-dish-to-meal', meal.slug)

@login_required
def add_music(request, slug):
    meal=get_object_or_404(Meal, slug=slug)
    form=AddMusicForm()
    if request.method =='POST':
        form=AddMusicForm(request.POST)
        if form.is_valid():
            music=form.save()
            music.group = meal.group
            music.meal.add(meal)
            music.save()
            return redirect('all-meals')

    return render(request, 'meals/add-music.html', {'form':form})

@login_required
def group_musics(request, slug):
    group = get_object_or_404(CustomGroup, slug=slug)
    musics = Music.objects.filter(group=group)

    context = {'musics': musics,
               'group': group}
    return render(request, 'meals/all-musics.html', context=context)

@login_required
def edit_music(request, id):
    music= get_object_or_404(Music, pk=id)
    form = AddMusicForm(instance=music)

    if request.method == 'POST':
        form = AddMusicForm(request.POST, instance=music)
        music = form.save()
        return redirect('group-musics', music.group.slug)
    
    return render(request, 'meals/add-music.html', {'form':form, 'music':music})

@login_required
def delete_music(request, id):
    music = get_object_or_404(Music, pk=id)
    music.delete()
    return redirect('all-meals')

@login_required
def add_anecdote(request, slug):
    meal=get_object_or_404(Meal, slug=slug)
    form=AddAnecdoteForm()
    if request.method =='POST':
        form=AddAnecdoteForm(request.POST)
        if form.is_valid():
            anecdote=form.save()
            anecdote.group=meal.group
            anecdote.date=meal.eaten_at
            anecdote.meal.add(meal)
            anecdote.save()
            return redirect('all-meals')

    return render(request, 'meals/add-anecdote.html', {'form':form})

@login_required
def edit_anecdote(request, id):
    anecdote= get_object_or_404(Anecdote, pk=id)
    form = AddAnecdoteForm(instance=anecdote)

    if request.method == 'POST':
        form = AddAnecdoteForm(request.POST, instance=anecdote)
        anecdote = form.save()
        return redirect('all-meals')
    
    return render(request, 'meals/add-anecdote.html', {'form':form, 'anecdote':anecdote})

@login_required
def delete_anecdote(request, id):
    anecdote = get_object_or_404(Anecdote, pk=id)
    anecdote.delete()
    return redirect('all-meals')

@login_required
def group_anecdotes(request, slug):
    group = get_object_or_404(CustomGroup, slug=slug)
    anecdotes = Anecdote.objects.filter(group=group)

    context = {'anecdotes': anecdotes,
               'group': group}
    return render(request, 'meals/all-anecdotes.html', context=context)

@login_required
def all_meals(request):
    group = get_groups(request.user)
    if group is None: 
        return redirect('all-groups')
    else:
        groups = CustomGroup.objects.filter(members__id__contains=request.user.id)
        for group in groups:
            meals = Meal.objects.filter(group__members__id__contains = request.user.id).distinct()
            meals = meals.order_by('-eaten_at')
            for meal in meals:
                musics = meal.meal_musics.all()
                print(musics)
    
    


        context={
            'meals':meals,
            'groups':groups,
        }

        return render(request, "meals/all-meals.html", context=context )
    
@login_required
def group_meals(request, slug):
    group = get_object_or_404(CustomGroup, slug=slug)
    meals = Meal.objects.filter(group=group)
    meals = meals.order_by('-eaten_at')

    context = {'meals': meals,
               'group': group}
    return render(request, 'meals/all-meals.html', context=context)

@login_required
def meal_detail_guest(request, slug, guest):
    meal = get_object_or_404(Meal, slug=slug)
    guest = get_object_or_404(User, slug=guest)

    context = {'meal':meal,
               'guest': guest}

    return render(request, "meals/meal-detail-with-guest.html", context=context)

@login_required
def invite_guest(request,slug):
    meal = get_object_or_404(Meal, slug = slug)
    group = meal.group
    form = GuestRegistrationForm()

    if request.method == "POST":
        form = GuestRegistrationForm(request.POST)
        if form.is_valid():
            guest = form.save(commit=False)
            guest.email = str(guest.pseudo) + "123@false-email.com"
            guest.username = str(guest.pseudo) + "123"
            print(guest.email)
            guest.is_rgpd = True
            guest.is_guest = True
            guest.save()
            guest.email = str(guest.slug) + "@false-email.com"
            guest.username = str(guest.slug)
            guest.save()
            group.members.add(guest)
            group.save()
            meal.guests.add(guest)
            meal.save()
            
            
            return redirect('meal-detail-guest', slug=meal.slug, guest=guest.slug)
        
    return render(request, 'meals/invite-guest.html',{'form': form})
