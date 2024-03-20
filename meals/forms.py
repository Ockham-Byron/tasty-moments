import math
from itertools import chain
import uuid
from django.core.exceptions import ValidationError
from django import forms
from django.utils.encoding import force_str
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from bootstrap_datepicker_plus.widgets import DatePickerInput
from .models import Dish, Comment, Meal, Music, Anecdote
from groups.models import CustomGroup

User=get_user_model()

class ColumnCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Widget that renders multiple-select checkboxes in columns.
    Constructor takes number of columns and css class to apply
    to the <ul> elements that make up the columns.
    """
    def __init__(self, columns=2, css_class=None, wrapper_css_class=None, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.columns = columns
        self.css_class = css_class
        self.wrapper_css_class = wrapper_css_class

    def render(self, name, value, attrs=None, renderer=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, {'name':name})
        choices_enum = list(enumerate(chain(self.choices, choices)))
        
        # This is the part that splits the choices into columns.
        # Slices vertically.  Could be changed to slice horizontally, etc.
        column_sizes = columnize(len(choices_enum), self.columns)
        columns = []
        for column_size in column_sizes:
            columns.append(choices_enum[:column_size])
            choices_enum = choices_enum[column_size:]
        output = []
        for column in columns:
            if self.css_class:
                output.append(u'<ul class="%s">' % self.css_class)
            else:
                output.append(u'<ul>')
            # Normalize to strings
            str_values = set([force_str(v) for v in value])
            for i, (option_value, option_label) in column:
                # If an ID attribute was given, add a numeric index as a suffix,
                # so that the checkboxes don't all have the same ID attribute.
                if has_id:
                    final_attrs = dict(final_attrs, id='%s_%s' % (
                            attrs['id'], i))
                    label_for = u' for="%s"' % final_attrs['id']
                else:
                    label_for = ''

                cb = forms.CheckboxInput(
                    final_attrs, check_test=lambda value: value in str_values)
                option_value = force_str(option_value)
                rendered_cb = cb.render(name, option_value)
                option_label = conditional_escape(force_str(option_label))
                output.append(u'<li><label%s>%s %s</label></li>' % (
                        label_for, rendered_cb, option_label))
            output.append(u'</ul>')
        
        if self.wrapper_css_class:
            wrapper = u'<div class="%s">%s</div>' % \
                (self.wrapper_css_class, u'\n'.join(output))
        else:
            wrapper = u'<div>%s</div>' % self.wrapper_css_class

        return mark_safe(wrapper)


def columnize(items, columns):
    """
    Return a list containing numbers of elements per column if `items` items
    are to be divided into `columns` columns.
    >>> columnize(10, 1)
    [10]
    >>> columnize(10, 2)
    [5, 5]
    >>> columnize(10, 3)
    [4, 3, 3]
    >>> columnize(3, 4)
    [1, 1, 1, 0]
    """
    elts_per_column = []
    for col in range(columns):
        col_size = int(math.ceil(float(items) / columns))
        elts_per_column.append(col_size)
        items -= col_size
        columns -= 1
    return elts_per_column

class AddDishForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'placeholder': _("Name of the Dish")}))
    chef=forms.ModelMultipleChoiceField(widget=ColumnCheckboxSelectMultiple(columns=3, css_class='col-md-4', wrapper_css_class='row',), queryset=User.objects.none(), required=None)
    picture=forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model=Dish
        fields=['name', 'chef', 'picture']

    def __init__(self, group, *args, **kwargs):
        super(AddDishForm, self).__init__(*args, **kwargs)
        members = group.members.all()
        chefs = members.exclude(is_guest=True)
        self.fields['chef'].queryset=chefs

class AddMealForm(forms.ModelForm):
    dishes = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Dish.objects.all(),
        widget=ColumnCheckboxSelectMultiple(columns=3, css_class='col-md-4', wrapper_css_class='row',)
    )
    picture=forms.ImageField(widget=forms.FileInput, required=False)
    eaten_at = forms.DateField(widget=DatePickerInput(options={
        "format": "DD/MM/YYYY",
        "showTodayButton": True,
        }))
    group = forms.ModelChoiceField(
        required=True, 
        queryset=CustomGroup.objects.none(), 
        
    )

    class Meta:
        model=Meal
        fields=['dishes', 'picture', 'eaten_at', 'group']
    
    def __init__(self, user, *args, **kwargs):
        super(AddMealForm, self).__init__(*args, **kwargs)
        
        self.fields['group'].queryset=user.group_members.all()

    
    

class AddCommentForm(forms.ModelForm):
    CHOICES = [(i,i) for i in range(11)]
    message=forms.CharField(widget=forms.Textarea(attrs={'rows':4, 'placeholder': _("Comment")}))
    rating=forms.TypedChoiceField(coerce=int, choices=CHOICES)

    class Meta:
        model=Comment
        fields=['message', 'rating']

class AddMusicForm(forms.ModelForm):
    title=forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':_("Title")
    }))
    artist=forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':_("Artist")
    }))

    class Meta:
        model=Music
        fields=['title', 'artist']

class AddAnecdoteForm(forms.ModelForm):
    message=forms.CharField(widget=forms.Textarea(attrs={
        'rows':10,
        'placeholder':_("Anecdote")
    }))
    

    class Meta:
        model=Anecdote
        fields=['message']


class GuestRegistrationForm(forms.ModelForm):
    pseudo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-right-0', 'placeholder': _('Username'), 'autocomplete':"username"}),)
    
    
    
    class Meta:
        model = User
        fields = ['pseudo']