from django.core.management import setup_environ  
import settings
setup_environ(settings)
from django.core.mail import send_mail
from flowspy.flowspec.models import *
from django.template.loader import render_to_string
import datetime


def notify_expired():
    routes = Route.objects.all()
    for route in routes:
        if route.status not in ['EXPIRED', 'ADMININACTIVE', 'ERROR']:
            expiration_days = (route.expires - datetime.date.today()).days
            if expiration_days < settings.EXPIRATION_NOTIFY_DAYS:
                try:
                    mail_body = render_to_string("rule_expiration.txt",
                                             {"route": route, 'expiration_days':expiration_days})
                    days_num = ' days'
                    expiration_days_text = "%s %s" %('in',expiration_days)
                    if expiration_days == 0:
                        days_num = ' today'
                        expiration_days_text = ''
                    if expiration_days == 1:
                        days_num = ' day'
                    send_mail(settings.EMAIL_SUBJECT_PREFIX + "Rule %s expires %s%s" %
                              (route.name,expiration_days_text, days_num),
                              mail_body, settings.SERVER_EMAIL,
                              [route.applier.email])
                except Exception as e:
                    print e
                    pass

if __name__ == "__main__":
    notify_expired()

