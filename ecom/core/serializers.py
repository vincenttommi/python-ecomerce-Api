from rest_framework import serializers
from .models import User,Profile,Product
from rest_framework.exceptions import AuthenticationFailed
from  django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode 
from django.utils.encoding import smart_str,smart_bytes,force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email
from  rest_framework_simplejwt.tokens import RefreshToken,TokenError


from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Profile  # Import your models

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    accountType = serializers.ChoiceField(choices=[('user', 'User'), ('admin', 'Admin'), ('instructor', 'Instructor')], required=True)

    # Read fields from Profile
    country = serializers.CharField(source="profile.country", required=True)
    countryCode = serializers.CharField(source="profile.countryCode", required=True)
    state = serializers.CharField(source="profile.state", required=True)
    address = serializers.CharField(source="profile.address", required=True)
    phoneNumber = serializers.CharField(source="profile.phoneNumber", required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'accountType',
                  'country', 'countryCode', 'state', 'address', 'phoneNumber']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})  # Extract profile data
        password = validated_data.pop('password')
        validated_data.pop('password2')  # Remove password2 since it's not in the User model

        # Create User
        user = User.objects.create(
            **validated_data,
            password=make_password(password)  # Hash password
        )

        # Create Profile and link it to the User
        Profile.objects.create(user=user, **profile_data)

        return user

    def to_representation(self, instance):
        """ Modify response to include profile fields """
        data = super().to_representation(instance)

        # Get related profile
        try:
            profile = instance.profile
            data.update({
                "country": profile.country,
                "countryCode": profile.countryCode,
                "state": profile.state,
                "address": profile.address,
                "phoneNumber": profile.phoneNumber
            })
        except Profile.DoesNotExist:
            pass  # If no profile exists, skip this step

        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    name = serializers.CharField(max_length=255, read_only=True)  # No changes here
    role = serializers.CharField(max_length=68, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    account_type = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        fields = ['email', 'password', 'name', 'role', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # User retrieval
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid credentials, try again')

        # Password check
        if not user.check_password(password):
            raise AuthenticationFailed('Invalid credentials, try again')

        # Check if user is verified
        if not user.is_verified:
            raise AuthenticationFailed('Your email is not verified. Please verify your email before logging in.')

        # Token generation
        user_token = user.tokens()  # Returns a dictionary with access and refresh tokens

        # Add user details to validated attrs
        attrs['name'] = user.full_name
        attrs['access_token'] = str(user_token.get('access'))
        attrs['refresh_token'] = str(user_token.get('refresh'))
        attrs['account_type'] = user.accountType  

        return attrs
         
class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    default_error_messages = {
        'bad_token': ('Token is Invalid or has expired')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')  # Fixed typo
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')

    
    

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():  # Use exists() for checking
            user = User.objects.get(email=email)
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
        
        
        
        



class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        # Check if the passwords match
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        # Decode the uidb64
        user_id = force_str(urlsafe_base64_decode(uidb64))
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found.")

        # Validate the token
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed('Reset link is invalid or expired.')

        # If everything is fine, return the user object
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        user.set_password(validated_data['password'])
        user.save()
        return user    
    
    
    
    
    

class productSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product    
        fields = ['title','price','tags','description','created_at']
        
    


