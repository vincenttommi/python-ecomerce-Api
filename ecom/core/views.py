from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import  IsAdminUser
from .serializers import  LogoutUserSerializer, PasswordResetRequestSerializer,  SetNewPasswordSerializer, LoginSerializer, UserRegistrationSerializer
from .models import OneTimePassword, User
from .utils import send_code_to_user
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class RegisterUser(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            try:
                send_code_to_user(user.email)  # Use `user.email` instead of `user['email']`
            except Exception as e:
                return Response({"error": "Email sending failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'data': serializer.data,
                'message': f'Hi {user.first_name}, thanks for signing up! A passcode has been sent to your email.'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyUserEmail(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        otp_code = request.data.get('otp')
        if not otp_code:
            return Response({"message": "Passcode not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_code_obj = OneTimePassword.objects.get(code=otp_code)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({"message": "Account verified successfully"}, status=status.HTTP_200_OK)
            return Response({"message": "User already verified"}, status=status.HTTP_200_OK)
        except OneTimePassword.DoesNotExist:
            return Response({"message": "Invalid passcode"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutUserView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LogoutUserSerializer

    def delete(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Logout successfully"}, status=status.HTTP_200_OK)


class PasswordResetConfirm(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"message": "Token is invalid or has expired"}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({"message": "Credentials are valid", "uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequest(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({"message": "A link has been sent to your email to reset your password."}, status=status.HTTP_200_OK)


class SetNewPassword(APIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






# class CreateProductView(APIView):
#     permission_classes = [IsAuthenticated, IsAdminUser]

#     def post(self, request):
#         logger.info(f"User: {request.user}, is_staff: {request.user.is_staff}, Authenticated: {request.user.is_authenticated}")
        
#         if not request.user.is_authenticated:
#             return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

#         if not request.user.is_staff:
#             return Response({"error": "User is not an admin"}, status=status.HTTP_403_FORBIDDEN)

#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             product = serializer.save()
#             return Response({
#                 "status": 201,
#                 "message": "Product created successfully",
#                 "data": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    