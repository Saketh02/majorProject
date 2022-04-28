import imp
from django.core.mail import send_mail
import os


send_mail(
    "Subject here",
    "Here is the message.",
    "sakethkalikota0@gmail.com",
    ["18211a1253@bvrit.ac.in"],
    fail_silently=True,
)