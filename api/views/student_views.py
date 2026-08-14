from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers import userSerializers, studentSerializer, teacherSerializer, roleSerializer
from ..models import User, Student, Teacher, Role

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def student_api(request, pk=None):
    if request.method == "GET":
        id = pk
        if id is not None:
            stu = Student.objects.get(id=id)   
            serializer = studentSerializer(stu)
            return Response(serializer.data)
        stu = Student.objects.all()
        serializer = studentSerializer(stu, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = studentSerializer(data = request.data )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)

    if request.method == "PUT":
        id = pk
        stu = Student.objects.get(pk = id)
        serializer = studentSerializer(stu, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg' : 'Data is Updated'})
        return Response(serializer.errors)

    if request.method == "PATCH":
        id = pk
        stu = Student.objects.get(pk = id)
        serializer = studentSerializer(stu, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg' : 'Data is Updated'})
        return Response(serializer.errors)

    if request.method == "DELETE":
        id = pk
        stu = Student.objects.get(pk = id)
        if stu is None:
            return Response({'msg' : 'Data is Not Found'})
        stu.delete()
        return Response({'msg' : 'Data is Deleted'})

        

