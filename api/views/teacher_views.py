from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers import teacherSerializer
from ..models import Teacher

@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

def teacher_api(request, pk = None):
    if request.method == "GET":
        id = pk
        if id is not None:
            teach = Teacher.objects.get(id = id)
            serializer = teacherSerializer(teach)
            return Response([serializer.data])
        teach = Teacher.objects.all()
        serializer = teacherSerializer(teach)
        return Response([serializer.data])

    if request.method == "POST":
        serializer = teacherSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.error)
    
    if request.method == "PUT":
        pk = id
        teach = Teacher.objects.get(id = pk)
        serializer = teacherSerializer(teach, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg' : 'data is updated'})
        return Response(serializer.error)

    if request.method == "DELETE":
        pk = id
        teach = Teacher.objects.get(id=pk)
        if teach is None:
            return Response({'msg' : 'Data is Not Found'})
        teach.delete()
        return Response({'msg' : 'Delete the Data'})



