from rest_framework import serializers
from .models import User



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=20, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=20, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password2', 'name', 'account_type', 'country',
            'country_code', 'state', 'address', 'phone_number'
        ]

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            account_type=validated_data['account_type'],
            country=validated_data['country'],
            country_code=validated_data['country_code'],
            state=validated_data['state'],
            address=validated_data['address'],
            phone_number=validated_data['phone_number']
        )

        return user 

