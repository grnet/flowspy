from django.conf import settings
# This patch was retrieved from: https://github.com/GoodCloud/django-longer-username
def MAX_USERNAME_LENGTH():
    if hasattr(settings,"MAX_USERNAME_LENGTH"):
        return settings.MAX_USERNAME_LENGTH
    else:
        return 255
