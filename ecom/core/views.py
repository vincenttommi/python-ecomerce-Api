from rest_framework import status
from rest_framework.response import Response 
from rest_framework.views import APIView
from .serializers import RegisterSerializer   




class RegisterUser(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"status": 400, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)