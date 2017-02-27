from django.core.management.base import BaseCommand

from payment.models import *
from courses.models import *

import logging

log = logging.getLogger('tq')


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info('run management command: {}'.format(__file__))
        print(
            'the following subscriptions have the incorrect state CONFIRMED eventhough there is a valid subscription payment entry:')
        count = 0
        for sp in SubscriptionPayment.objects.all():
            s = sp.subscription
            if s.state == Subscribe.State.CONFIRMED and s.get_price_to_pay() == sp.amount:
                count += 1
                print("{} - {} - {}".format(s.id, s.usi, s))
                s.state = Subscribe.State.PAYED
                s.save()
        print('TOTAL fixed: {}'.format(count))