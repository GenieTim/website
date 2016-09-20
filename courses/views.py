from django.contrib.sessions.exceptions import SuspiciousSession
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView
from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import ugettext as _

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import *

from . import services

from django.contrib.auth.models import User
from django.utils import dateformat

from django.contrib.admin.views.decorators import staff_member_required

from django.views.generic.edit import FormView

import logging

log = logging.getLogger('tq')


# Create your views here.

def course_list(request, force_preview=False):
    template_name = "courses/list.html"
    context = {}

    # if unpublished courses should be shown with a preview marker
    preview_mode = request and request.user.is_staff or force_preview

    offerings = services.get_offerings_to_display(request, preview_mode)
    c_offerings = []
    for offering in offerings:
        offering_sections = []
        course_set = offering.course_set

        if offering.type == Offering.Type.REGULAR:
            for (w, w_name) in Weekday.CHOICES:
                section_dict = {}
                section_dict['section_title'] = WEEKDAYS_TRANS[w]
                section_dict['courses'] = [c for c in course_set.weekday(w) if c.is_displayed(preview_mode)]
                if (w in Weekday.WEEKEND) and section_dict['courses'].__len__() == 0:
                    pass
                else:
                    offering_sections.append(section_dict)

            # add courses that have no weekday entry yet
            section_dict = {}
            section_dict['section_title'] = _("Unknown weekday")
            section_dict['courses'] = course_set.weekday(None)
            if section_dict['courses'].__len__() != 0:
                offering_sections.append(section_dict)
        elif offering.type == Offering.Type.IRREGULAR:
            courses_by_month = course_set.by_month()
            for (d, l) in courses_by_month:
                if d is None:
                    section_title = _("Unknown month")
                elif 1 < d.month < 12:
                    # use the django formatter for date objects
                    section_title = dateformat.format(d, 'F Y')
                else:
                    section_title = ""
                # filter out undisplayed courses if not staff user
                if not preview and not request.user.is_staff:
                    l = [c for c in l if c.is_displayed()]
                # tracks if at least one period of a course is set (it should be displayed on page)
                deviating_period = False
                for c in l:
                    if c.period:
                        deviating_period = True
                        break

                offering_sections.append(
                    {'section_title': section_title, 'courses': l, 'hide_period_column': not deviating_period})
        else:
            message = "unsupported offering type"
            log.error(message)
            raise Http404(message)

        c_offerings.append({
            'offering': offering,
            'sections': offering_sections,
        })

    context.update({
        'offerings': c_offerings,
    })
    return render(request, template_name, context)


def course_list_preview(request):
    return course_list(request, force_preview=True)


def subscription(request, course_id):
    from .forms import UserForm, create_initial_from_user
    template_name = "courses/subscription.html"
    context = {}

    # do not clear session keys

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            request.session['user1_data'] = form.cleaned_data
            if not Course.objects.get(id=course_id).type.couple_course or ("subscribe_alone" in request.POST):
                return redirect('courses:subscription_do', course_id)
            elif "subscribe_partner" in request.POST:
                return redirect('courses:subscription2', course_id)
            else:
                return redirect('courses:subscription', course_id)

    # if a GET (or any other method) we'll create a blank form
    else:
        if request.user.is_authenticated():
            # overwrite initial values with those of the user and his profile
            initial = create_initial_from_user(request.user)
            form = UserForm(initial=initial)
        else:
            form = UserForm()

    context.update({
        'menu': "courses",
        'course': get_object_or_404(Course, id=course_id),
        'person': 1,
        'form': form
    })
    return render(request, template_name, context)


def subscription2(request, course_id):
    from .forms import UserForm
    if 'user1_data' not in request.session:
        # This can happen if a client does reload the page after the session was reset
        # -> Redirect to a page with an error message
        res = dict()
        res['tag'] = 'danger'
        res['text'] = _('The session is no longer valid. Please start over with the subscription.')
        res['long_text'] = None
        request.session['subscription_result'] = res
        return redirect('courses:subscription_message', course_id)

    template_name = "courses/subscription2.html"
    context = {}

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            request.session['user2_data'] = form.cleaned_data
            return redirect('courses:subscription_do', course_id)

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


def subscription_do(request, course_id):
    if 'user1_data' not in request.session:
        raise SuspiciousSession()

    if 'user2_data' in request.session:
        res = services.subscribe(course_id, request.session['user1_data'], request.session['user2_data'])
    else:
        res = services.subscribe(course_id, request.session['user1_data'], None)

    # clear session keys
    if 'user1_data' in request.session:
        del request.session['user1_data']
    if 'user2_data' in request.session:
        del request.session['user2_data']

    request.session['subscription_result'] = res
    return redirect('courses:subscription_message', course_id)


def subscription_message(request, course_id):
    if 'subscription_result' not in request.session:
        return redirect('courses:subscription', course_id)

    template_name = "courses/subscription_message.html"
    context = {}

    context.update({
        'menu': "courses",
        'message': request.session['subscription_result'],
        'course': Course.objects.get(id=course_id),
    })
    return render(request, template_name, context)


@staff_member_required
def confirmation_check(request):
    template_name = "courses/confirmation_check.html"
    context = {}

    context.update({
        'subscriptions': Subscribe.objects.accepted().select_related().filter(
            confirmations__isnull=True).all()
    })
    return render(request, template_name, context)


@staff_member_required
def duplicate_users(request):
    template_name = "courses/duplicate_users.html"
    context = {}
    users = []
    user_aliases = dict()

    # if this is a POST request we need to process the form data
    if request.method == 'POST' and 'post' in request.POST and request.POST['post'] == 'yes':
        duplicates_ids = request.session['duplicates']
        to_merge = dict()
        for primary_id, aliases_ids in duplicates_ids.iteritems():
            to_merge_aliases = []
            for alias_id in aliases_ids:
                key = '{}-{}'.format(primary_id, alias_id)
                if key in request.POST and request.POST[key] == 'yes':
                    to_merge_aliases.append(alias_id)
            if to_merge_aliases:
                to_merge[primary_id] = to_merge_aliases
        log.info(to_merge)
        services.merge_duplicate_users_by_ids(to_merge)
    else:
        duplicates = services.find_duplicate_users()
        for primary, aliases in duplicates.iteritems():
            users.append(User.objects.get(id=primary))
            user_aliases[primary] = list(User.objects.filter(id__in=aliases))

        # for use when form is submitted
        request.session['duplicates'] = duplicates

    context.update({
        'users': users,
        'user_aliases': user_aliases
    })
    return render(request, template_name, context)


# helper function
def offering_place_chart_dict(offering):
    labels = []
    series_confirmed = []
    series_men_count = []
    series_women_count = []
    series_free = []
    courses = offering.course_set.all()

    for course in courses:
        # NOTE: do not use the related manager with 'course.subscriptions', because does not have access to default manager methods
        subscriptions = Subscribe.objects.filter(course=course)
        labels.append(u'<a href="{}">{}</a>'.format(reverse('courses:course_overview', args=[course.id]),
                                                    course.name))
        accepted_count = subscriptions.accepted().count()
        series_confirmed.append(str(accepted_count))
        mc = subscriptions.new().men().count()
        wc = subscriptions.new().women().count()
        series_men_count.append(str(mc))
        series_women_count.append(str(wc))
        maximum = course.max_subscribers
        if maximum:
            freec = max(0, maximum - accepted_count - mc - wc)
        else:
            freec = 0
        series_free.append(str(freec))

    return {
        'labels': labels,
        'series_confirmed': series_confirmed,
        'series_men': series_men_count,
        'series_women': series_women_count,
        'series_free': series_free,
        'height': 25 * len(labels) + 90,
    }


# helper function
def offering_time_chart_dict(offering):
    traces = []
    for c in offering.course_set.all():
        trace = dict()
        trace['name'] = c.name
        trace['x'] = []
        trace['y'] = []
        counter = 0
        last = None
        for s in c.subscriptions.order_by('date').all():
            if last is None:
                last = s.date.date()
            if s.date.date() == last:
                counter += 1
            else:
                # save temp
                trace['x'].append(str(s.date.date()))
                trace['y'].append(counter)
                counter += 1
                last = s.date.date()
        if last is not None:
            trace['x'].append(str(last))
            trace['y'].append(counter)
        traces.append(trace)

    trace_total = dict()
    trace_total['x'] = []
    trace_total['y'] = []
    counter = 0
    last = None
    for s in Subscribe.objects.filter(course__offering__id=offering.id).order_by('date').all():
        if last is None:
            last = s.date.date()
        if s.date.date() == last:
            counter += 1
        else:
            # save temp
            print("add counter {}".format(counter))
            trace_total['x'].append(str(s.date.date()))
            trace_total['y'].append(counter)
            counter += 1
            last = s.date.date()
    if last is not None:
        trace_total['x'].append(str(last))
        trace_total['y'].append(counter)

    print(trace_total['x'])
    print(trace_total['y'])

    return {
        'traces': traces,
        'trace_total': trace_total,
    }


@staff_member_required
def subscription_overview(request):
    template_name = "courses/auth/subscription_overview.html"
    context = {}

    offering_charts = []
    for o in services.get_offerings_to_display(request):
        offering_charts.append({'offering': o, 'place_chart': offering_place_chart_dict(o)})

    context.update({
        'offering_charts': offering_charts,
        'all_offerings': services.get_all_offerings()
    })
    return render(request, template_name, context)


@staff_member_required
def course_overview(request, course_id):
    template_name = "courses/auth/course_overview.html"
    context = {}

    course = Course.objects.get(id=course_id)
    # NOTE: do not use the related manager with 'course.subscriptions', because does not have access to default manager methods
    subscriptions = Subscribe.objects.filter(course=course)

    cc = subscriptions.accepted().count()
    mc = subscriptions.new().men().count()
    wc = subscriptions.new().women().count()
    maximum = course.max_subscribers
    if maximum:
        freec = max(0, maximum - cc - mc - wc)
    else:
        freec = 0

    context['course'] = course
    context['place_chart'] = {
        'label': course.name,
        'confirmed': cc,
        'men': mc,
        'women': wc,
        'free': freec,
        'total': cc + mc + wc + freec
    }
    return render(request, template_name, context)


@staff_member_required
def offering_overview(request, offering_id):
    template_name = "courses/auth/offering_overview.html"
    context = {}

    o = Offering.objects.get(id=offering_id)

    context['offering'] = o
    context['place_chart'] = offering_place_chart_dict(o)
    context['time_chart'] = offering_time_chart_dict(o)
    return render(request, template_name, context)


@method_decorator(login_required, name='dispatch')
class ProfileView(FormView):
    from .forms import UserEditForm
    template_name = 'courses/auth/profile.html'
    form_class = UserEditForm
    success_url = reverse_lazy('auth_profile')

    def get_initial(self):
        from .forms import create_initial_from_user
        initial = create_initial_from_user(self.request.user)

        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProfileView, self).get_context_data(**kwargs)

        user = self.request.user
        if user.profile.gender:
            context['gender_icon'] = 'mars' if user.profile.gender == 'm' else 'venus'
        return context

    def form_valid(self, form):
        services.update_user(self.request.user, form.cleaned_data)
        return super(ProfileView, self).form_valid(form)
