from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import TemplateView, ListView
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from models import *

from forms import *

from services import *

import logging
log = logging.getLogger('courses')

# Create your views here.

def course_list(request):
    template_name = "courses/list.html"
    context={}
    
    course_set=Offering.objects.get(name='HS 2014 Q1').course_set
    weekday_list = []
    for (w,w_name) in WEEKDAYS:
        weekday_dict = {}
        weekday_dict['weekday']=w_name
        weekday_dict['courses']=course_set.weekday(w)
        if (w=='sat' or w=='sun') and weekday_dict['courses'].__len__() == 0:
            pass
        else:
            weekday_list.append(weekday_dict)
    
    #add courses that have no weekday entry yet
    weekday_dict = {}
    weekday_dict['weekday']=_("Unknown weekday")
    weekday_dict['courses']=course_set.weekday(None)
    if weekday_dict['courses'].__len__() != 0:
        weekday_list.append(weekday_dict)
        
    context.update({
        'menu': "courses",
        'weekday_list': weekday_list,
    })
    return render(request, template_name, context)

def subscription(request, course_id):
    template_name = "courses/subscription.html"
    context={}
    
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            request.session['user1_data']=form.cleaned_data
            return redirect('courses:subscription2', course_id)

    # if a GET (or any other method) we'll create a blank form
    else:
        initial = {'newsletter': True}
        form = UserForm(initial=initial)

    context.update({
            'menu': "courses",
            'course': Course.objects.get(id=course_id),
            'person': 1,
            'form': form
        })
    return render(request, template_name, context)


def subscription2(request, course_id):
    template_name = "courses/subscription2.html"
    context={}
    
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            request.session['user2_data']=form.cleaned_data
            return redirect('courses:subscription_done', course_id)

    # if a GET (or any other method) we'll create a blank form
    else:
        initial = {'newsletter': True}
        form = UserForm(initial=initial)

    context.update({
            'menu': "courses",
            'course': Course.objects.get(id=course_id),
            'person': 2,
            'form': form
        })
    return render(request, template_name, context)

def subscription_done(request, course_id):
    template_name = "courses/subscription_done.html"
    context={}
    
    subscribe(request.session['user1_data'], request.session['user2_data'])

    context.update({
            'menu': "courses",
            'course': Course.objects.get(id=course_id),
        })
    return render(request, template_name, context)