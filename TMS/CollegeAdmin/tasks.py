from TMS.celery import app
from django.core.mail import send_mail


@app.task
def sendEmailNotifs(subject, message, recipients):
    send_mail(
        subject, message, "sakethkalikota02@gmail.com", recipients, fail_silently=False
    )


# Command for turning celery job processor on: celery worker -A TMS -l info --pool=solo
# To add emails from your email, make following changes
# step-1: login to the account in chrome
# step-2: goto myaccount.google.com/lesssecureapps and turn it on
# step-3: goto accounts.google.com/DisplayUnlockCaptcha and provide access
# step-4: change email host name and password in settings.py
