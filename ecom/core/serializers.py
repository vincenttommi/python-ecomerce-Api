from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode 
from django.utils.encoding import smart_str,smart_bytes,force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'account_type', 'country', 'state', 'phone_number']
        
        
        



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        if CustomUser.objects.filter(email=email).exists():  # Use exists() for checking
            user = CustomUser.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            # Accessing the request context properly
            request = self.context.get('request')
            site_domain = get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            abslink = f"http://{site_domain}{relative_link}"
            email_body = f"Hi, use the link below to reset your password:\n{abslink}"

            data = {
                'email_body': email_body,
                'email_subject': "Reset your password",
                'to_email': user.email
            }
            send_normal_email(data)
        else:
            raise serializers.ValidationError("User with this email does not exist.")
        
        return attrs
        
            
                  