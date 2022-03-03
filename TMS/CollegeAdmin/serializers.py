from rest_framework import serializers
from .models import Bus


class addBusDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = [
            "id",
            "name",
            "number",
            "driverName",
            "driverMobile",
            "inchargeName",
            "inchargeContact",
            "seats",
        ]