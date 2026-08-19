from rest_framework import serializers
from django.db import transaction
from .models import Role, Student, Teacher, User


class roleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class userSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'role_name']

    def validate_email(self, value):
        email = value.lower()
        queryset = User.objects.filter(email=email)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('This email is already registered.')
        return email

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class registerSerializer(userSerializers):
    roll_no = serializers.IntegerField(write_only=True, required=False)
    roll_number = serializers.IntegerField(write_only=True, required=False)
    std = serializers.IntegerField(write_only=True, required=False)
    subject = serializers.CharField(write_only=True, required=False, max_length=25)

    class Meta(userSerializers.Meta):
        fields = userSerializers.Meta.fields + ['roll_no', 'roll_number', 'std', 'subject']

    def validate_role(self, value):
        if value and value.role_name == 'Admin':
            raise serializers.ValidationError('Admin users cannot be created from public registration.')
        return value

    def validate(self, attrs):
        role = attrs.get('role')
        role_name = getattr(role, 'role_name', None)

        if role_name == 'Student':
            roll_no = attrs.get('roll_no', attrs.get('roll_number'))
            if roll_no is None:
                raise serializers.ValidationError({'roll_no': 'This field is required for student registration.'})
            if attrs.get('std') is None:
                raise serializers.ValidationError({'std': 'This field is required for student registration.'})
            if Student.objects.filter(roll_no=roll_no, std=attrs.get('std')).exists():
                raise serializers.ValidationError({
                    'roll_no': 'This roll number is already registered for this standard.'
                })

        if role_name == 'Teacher' and not attrs.get('subject'):
            raise serializers.ValidationError({'subject': 'This field is required for teacher registration.'})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        roll_no = validated_data.pop('roll_no', None)
        roll_number = validated_data.pop('roll_number', None)
        std = validated_data.pop('std', None)
        subject = validated_data.pop('subject', None)

        user = super().create(validated_data)
        role_name = getattr(user.role, 'role_name', None)

        if role_name == 'Student':
            Student.objects.create(user=user, roll_no=roll_no or roll_number, std=std)
        elif role_name == 'Teacher':
            Teacher.objects.create(user=user, subject=subject)

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        role_name = getattr(instance.role, 'role_name', None)

        if role_name == 'Student' and hasattr(instance, 'student'):
            data['student'] = {
                'id': instance.student.id,
                'roll_no': instance.student.roll_no,
                'std': instance.student.std,
            }

        if role_name == 'Teacher' and hasattr(instance, 'teacher'):
            data['teacher'] = {
                'id': instance.teacher.id,
                'subject': instance.teacher.subject,
            }

        return data


class studentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'username', 'email', 'roll_no', 'std']
        extra_kwargs = {'user': {'required': False}}

    def validate(self, attrs):
        roll_no = attrs.get('roll_no', getattr(self.instance, 'roll_no', None))
        std = attrs.get('std', getattr(self.instance, 'std', None))

        queryset = Student.objects.filter(roll_no=roll_no, std=std)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError({
                'roll_no': 'This roll number is already registered for this standard.'
            })
        return attrs


class teacherSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'username', 'email', 'subject']
        extra_kwargs = {'user': {'required': False}}


class studentRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ['id', 'username', 'email', 'password', 'roll_no', 'std']

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already registered.')
        return email

    def validate(self, attrs):
        if Student.objects.filter(roll_no=attrs.get('roll_no'), std=attrs.get('std')).exists():
            raise serializers.ValidationError({
                'roll_no': 'This roll number is already registered for this standard.'
            })
        return attrs

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        # Look up the Student role
        student_role = Role.objects.get(role_name='Student')

        user = User(username=username, email=email, role=student_role)
        user.set_password(password)
        
        user.save()

        student = Student.objects.create(user=user, **validated_data)
        return student

    def to_representation(self, instance):
        # Return the created student with useful nested info
        return {
            'id': instance.id,
            'username': instance.user.username,
            'email': instance.user.email,
            'roll_no': instance.roll_no,
            'std': instance.std,
        }


class teacherRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'username', 'email', 'password', 'subject']

    def validate_email(self, value):
        return value.lower()

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        teacher_role = Role.objects.get(role_name='Teacher')

        user = User(username=username, email=email, role=teacher_role)
        user.set_password(password)
        user.save()

        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.user.username,
            'email': instance.user.email,
            'subject': instance.subject,
        }
