from TMS.celery import app
from django.core.mail import send_mail


@app.task
def sendEmailNotifs(subject, message, recipients):
    send_mail(
        subject, message, "sakethkalikota02@gmail.com", recipients, fail_silently=True
    )
