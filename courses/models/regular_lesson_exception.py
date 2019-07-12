from django.db import models
from django.db.models import CASCADE

from courses.models import Weekday


class RegularLessonException(models.Model):
    regular_lesson = models.ForeignKey('RegularLesson', related_name='exceptions', on_delete=CASCADE)
    date = models.DateField(blank=False, null=True)
    date.help_text = "Date of the exception"
    is_cancellation = models.BooleanField(null=False, blank=False, default=False)
    is_cancellation.help_text = "Cancellation of the regular lesson on the given date. " \
                                "No other fields need to be specified."
    time_from = models.TimeField(null=True, blank=True)
    time_from.help_text = "Only set, if different"
    time_to = models.TimeField(null=True, blank=True)
    time_to.help_text = "Only set, if different"

    lesson_details = models.OneToOneField('LessonDetails', related_name='regular_lesson_exception',
                                          null=True, blank=True, on_delete=CASCADE)
    lesson_details.help_text = "Only needed, if details are different from course. " \
                               "E.g. different room, different teachers,..."

    def get_time_from(self):
        return self.time_from or self.regular_lesson.time_from

    def get_time_to(self):
        return self.time_to or self.regular_lesson.time_to

    def is_applicable(self):
        period = self.regular_lesson.course.get_period()

        return self.date.weekday() == Weekday.NUMBERS[self.regular_lesson.weekday] and \
               period.date_from <= self.date <= period.date_to

    class Meta:
        ordering = ['date']

    def __str__(self):
        return "Exception on {}".format(self.date.strftime('%d.%m.%Y'))
