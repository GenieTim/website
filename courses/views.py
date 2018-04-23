import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.exceptions import SuspiciousSession
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import dateformat
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.views.generic.edit import FormView

from . import services
from .models import *

log = logging.getLogger('tq')


# Create your views here.

def course_list(request, force_preview=False):
    template_name = "courses/list.html"
    context = {}

    # unpublished courses should be shown with a preview marker
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
            section_dict['section_title'] = _("Irregular weekday")
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
                l = [c for c in l if c.is_displayed(preview_mode)]
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

@login_required
def subscription(request, course_id):
    from .forms import SingleSubscriptionForm, CoupleSubscriptionForm
    template_name = "courses/subscription.html"

    # do not clear session keys
    course = Course.objects.filter(id=course_id)
    
    # if there is no course with this id --> redirect user to course list
    if len(course) == 0:
        return redirect('courses:course_list')
    # the course id must be unique; this is a consistency check
    assert len(course) == 1
    course = course[0]
    
    is_couple_course = course.type.couple_course
    
    # create the correct form instance
    if is_couple_course:
        form = CoupleSubscriptionForm(request.POST)
    else:
        form = SingleSubscriptionForm(request.POST)
    
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            assert request.user != None
            data = {
                'user_id1': request.user.id,
                'experience': form.cleaned_data['experience'],
                'comment': form.cleaned_data['comment'],
            }
            if form.cleaned_data['partner_email']:
                partner = UserProfile.objects.filter(user__email=form.cleaned_data['partner_email'])
                assert len(partner) == 1    # there should only be one partner with this email address
                partner = partner[0]
                data['user_id2'] = partner.user.id
            
            request.session['data'] = data
            if 'subscribe' in request.POST:
                return redirect('courses:subscription_do', course_id)
            else:
                # no valid submit button value
                return redirect('courses:subscription', course_id)

    context = {}
    context.update({
        'menu': "courses",
        'course': get_object_or_404(Course, id=course_id),
        'form': form
    })
    return render(request, template_name, context)

@login_required
def subscription_do(request, course_id):
    if 'data' not in request.session:
        raise SuspiciousSession()

    res = services.subscribe(course_id, request.session['data'])

    # clear session keys
    if 'data' in request.session:
        del request.session['data']

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
        for primary_id, aliases_ids in duplicates_ids.items():
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
        for primary, aliases in duplicates.items():
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
                                                    escape(course.name)))
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


def progress_chart_dict():
    labels = []
    series_couple = []
    series_single = []

    for o in Offering.objects.filter(type=Offering.Type.REGULAR).all():
        subscriptions = Subscribe.objects.filter(course__offering=o)
        labels.append(u'<a href="{}">{}</a>'.format(reverse('courses:offering_overview', args=[o.id]),
                                                    escape(o.name)))
        accepted = subscriptions.accepted()
        total_count = accepted.count()
        couple_count = accepted.filter(matching_state=Subscribe.MatchingState.COUPLE).count()
        single_count = total_count - couple_count

        series_couple.append(str(couple_count))
        series_single.append(str(single_count))

    return {
        'labels': labels,
        'series_couple': series_couple,
        'series_single': series_single,
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
    
    ETH_count = len(Subscribe.objects.filter(user__profile__student_status = UserProfile.StudentStatus.ETH))
    UZH_count = len(Subscribe.objects.filter(user__profile__student_status = UserProfile.StudentStatus.UNI))
    PH_count = len(Subscribe.objects.filter(user__profile__student_status = UserProfile.StudentStatus.PH))
    other_count = len(Subscribe.objects.filter(user__profile__student_status = UserProfile.StudentStatus.OTHER))
    no_count = len(Subscribe.objects.filter(user__profile__student_status = UserProfile.StudentStatus.NO))
    
    university_chart = {
        'ETH_count': ETH_count,
        'UZH_count': UZH_count,
        'PH_count': PH_count,
        'no_count': no_count,
        'other_count': other_count,
    }

    context.update({
        'progress_chart': progress_chart_dict(),
        'offering_charts': offering_charts,
        'all_offerings': services.get_all_offerings(),
        'university_chart': university_chart
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


@staff_member_required
def export_summary(request):
    from courses import services
    return services.export_summary('csv')


@staff_member_required
def export_offering_summary(request, offering_id):
    from courses import services
    return services.export_summary('csv', [Offering.objects.filter(pk=offering_id).first()])


@staff_member_required
def export_offering_teacher_payment_information(request, offering_id):
    from courses import services
    return services.export_teacher_payment_information('csv', [Offering.objects.filter(pk=offering_id).first()])
