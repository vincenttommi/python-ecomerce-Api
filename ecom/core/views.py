from rest_framework import status
from rest_framework.response import Response 
from .serializers import RegisterSerializer   
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserSerializer
from core.utils import send_code_to_user




class RegisterUser(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
   
   
        return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"status": 400, "message": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)

        if user is None:
            return Response({"status": 400, "message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)  #converying refresh token to string

        return Response({
            "status": 200,
            "message": "Login successfully",
            "data": {
                "token": access_token,
                "refresh":refresh_token,
                "user": {
                    "email": user.email,
                    "name": user.name,
                    "accountType": user.account_type,
                    "country": user.country,
                    "state": user.state,
                    "phoneNumber": user.phone_number,   
                }
            }
        }, status=status.HTTP_200_OK)
        
        
        

class LogoutView(APIView):
    def delete(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()  # ✅ Blacklist token on logout
            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)        