from rest_framework import serializers
from .models import Student, Role, User, Teacher

class roleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class userSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)      # Hashes the password (PBKDF2) before the saving to the DB
        user.save()
        return user
        
class studentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class teacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'