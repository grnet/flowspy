from django.core.mail.message import EmailMessage
from django.conf import settings


def send_new_mail(subject, message, from_email, recipient_list, bcc_list):
    return EmailMessage(subject, message, from_email, recipient_list, bcc_list).send()


def get_peer_techc_mails(user, peer):
    mail = []
    additional_mail = []
    techmails_list = []
    user_mail = '%s' % user.email
    user_mail = user_mail.split(';')
    techmails = []
    if peer:
        techmails = peer.techc_emails.all()
    if techmails:
        for techmail in techmails:
            techmails_list.append(techmail.email)
    if settings.NOTIFY_ADMIN_MAILS:
        additional_mail = settings.NOTIFY_ADMIN_MAILS
    mail.extend(additional_mail)
    mail.extend(techmails_list)
    return mail
