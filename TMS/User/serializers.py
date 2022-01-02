from rest_framework import serializers
from .models import Register


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = [
            "id",
            "name",
            "rollnum",
            "email",
            "mobile",
            "department",
            "year",
            "password",
            "isAdmin",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = self.Meta.model(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user