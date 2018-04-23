from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from events.models import Event

import django.contrib.auth as auth

import logging
import datetime

log = logging.getLogger('tq')

# Create your views here.

@staff_member_required
def newsletter_list(request, newsletter=True):
    template_name = "export/newsletter.html"
    context = {}

    context.update({
        'users': auth.models.User.objects.filter(is_active=1, profile__newsletter=newsletter).all()
    })
    return render(request, template_name, context)


@staff_member_required
def no_newsletter_list(request):
    return newsletter_list(request, False)
