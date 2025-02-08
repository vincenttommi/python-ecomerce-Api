from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'name', 'account_type', 
            'country', 'country_code', 'state', 'address', 'phone_number'
        ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        """Custom response format without token"""
        return {
            "status": 201,
            "message": "User registered successfully",
            "data": {
                "user": {
                    "email": instance.email,
                    "name": instance.name,
                    "accountType": instance.account_type,
                    "country": instance.country,
                    "state": instance.state,
                    "phoneNumber": instance.phone_number,
                    "address": instance.address
                }
            }
        }
