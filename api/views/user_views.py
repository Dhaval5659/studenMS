from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import User, Role, Student, Teacher
from ..serializers import userSerializers

# Create your views here.

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

def user_api(request, pk=None):
    if request.method == 'GET':
        id = pk
        if id is not None:
            user = User.objects.get(id=id)
            serializer = userSerializers(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = User.objects.all()
        serializer = userSerializers(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
