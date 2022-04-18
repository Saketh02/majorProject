from distutils.archive_util import make_zipfile
from statistics import mode
from django.db import models
from django.db.models.deletion import CASCADE
from User.models import Register

# Create your models here.
class Bus(models.Model):
    name = models.CharField(max_length=15, unique=True)
    number = models.CharField(max_length=50, unique=True)
    driverName = models.CharField(max_length=255)
    driverMobile = models.CharField(max_length=20, unique=True)
    inchargeName = models.CharField(max_length=255)
    inchargeContact = models.CharField(max_length=50, unique=True)
    seats = models.IntegerField(default=45)

    REQUIRED_FIELDS = [
        "name",
        "number",
        "driverName",
        "driverMobile",
        "inchargeName",
        "inchargeContact",
    ]


class busStops(models.Model):
    bus = models.ManyToManyField(Bus)
    name = models.CharField(max_length=255)
    fee = models.IntegerField()

    REQUIRED_FIELDS = ["name", "fee"]


class busTimings(models.Model):
    bus = models.ForeignKey(Bus, on_delete=CASCADE)
    stop = models.ForeignKey(busStops, on_delete=CASCADE)
    time = models.TimeField()

    REQUIRED_FIELDS = ["time"]


class busRequest(models.Model):
    student = models.ForeignKey(Register, on_delete=CASCADE)
    stop = models.ForeignKey(busStops, on_delete=CASCADE)
    approvedStatus = models.BooleanField(default=False)


class busAllotmentData(models.Model):
    student = models.ForeignKey(Register, on_delete=CASCADE)
    bus = models.ForeignKey(Bus, on_delete=CASCADE)
    boardingPoint = models.ForeignKey(busStops, on_delete=CASCADE)
    seatNumber = models.IntegerField(null=False)
    paidAmount = models.IntegerField(default=0)
    paymentStatus = models.BooleanField(default=False)


class payment(models.Model):
    student = models.ForeignKey(Register, on_delete=CASCADE)
    orderId = models.CharField(max_length=150, unique=True, null=True)
    paymentId = models.CharField(max_length=150, unique=True, null=True)
    signature = models.CharField(max_length=200, unique=True, null=True)
