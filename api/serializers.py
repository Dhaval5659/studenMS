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
        if self.instance:                           # For Update use when it comes to duplicate
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('This email is already registered.')
        return email

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)             # Hash the Password
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
    std = serializers.IntegerField(write_only=True, required=False)
    subject = serializers.CharField(write_only=True, required=False, max_length=25)
    class_teacher_of = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta(userSerializers.Meta):
        fields = userSerializers.Meta.fields + ['roll_no', 'std', 'subject', 'class_teacher_of']

    def validate_role(self, value):
        if value and value.role_name == 'Admin':
            raise serializers.ValidationError('Admin users cannot be created from public registration.')
        return value

    def validate(self, attrs):
        role = attrs.get('role')
        role_name = getattr(role, 'role_name', None)

        if role_name == 'Student':
            roll_no = attrs.get('roll_no')
            if roll_no is None:
                raise serializers.ValidationError({'roll_no': 'This field is required for student registration.'})
            if attrs.get('std') is None:
                raise serializers.ValidationError({'std': 'This field is required for student registration.'})
            if Student.objects.filter(roll_no=roll_no, std=attrs.get('std')).exists():
                raise serializers.ValidationError({
                    'roll_no': 'This roll number is already registered for this standard.'
                })

        if role_name == 'Teacher':
            if not attrs.get('subject'):
                raise serializers.ValidationError({'subject': 'This field is required for teacher registration.'})

            class_teacher_of = attrs.get('class_teacher_of')
            if class_teacher_of is not None and Teacher.objects.filter(class_teacher_of=class_teacher_of).exists():
                raise serializers.ValidationError({
                    'class_teacher_of': f'A class teacher is already assigned for standard {class_teacher_of}.'
                })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        roll_no = validated_data.pop('roll_no', None)
        std = validated_data.pop('std', None)
        subject = validated_data.pop('subject', None)
        class_teacher_of = validated_data.pop('class_teacher_of', None)

        user = super().create(validated_data)
        role_name = getattr(user.role, 'role_name', None)

        if role_name == 'Student':
            Student.objects.create(user=user, roll_no=roll_no, std=std)
        elif role_name == 'Teacher':
            Teacher.objects.create(user=user, subject=subject, class_teacher_of=class_teacher_of)

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
                'class_teacher_of': instance.teacher.class_teacher_of,
            }

        return data


class studentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class_teacher = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'user', 'username', 'email', 'roll_no', 'std', 'class_teacher']
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

    def get_class_teacher(self, obj):
        teacher = Teacher.objects.filter(class_teacher_of=obj.std).select_related('user').first()
        if teacher:
            return {
                'id': teacher.id,
                'username': teacher.user.username,
                'email': teacher.user.email,
                'subject': teacher.subject,
            }
        return None


class teacherSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class_students = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'username', 'email', 'subject', 'class_teacher_of', 'class_students']
        extra_kwargs = {'user': {'required': False}}

    def validate(self, attrs):
        class_teacher_of = attrs.get('class_teacher_of', getattr(self.instance, 'class_teacher_of', None))
        if class_teacher_of is not None:
            queryset = Teacher.objects.filter(class_teacher_of=class_teacher_of)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({
                    'class_teacher_of': f'A class teacher is already assigned for standard {class_teacher_of}.'
                })
        return attrs

    def get_class_students(self, obj):
        if obj.class_teacher_of is None:
            return None
        students = Student.objects.filter(std=obj.class_teacher_of).select_related('user')
        return [
            {
                'id': student.id,
                'username': student.user.username,
                'roll_no': student.roll_no,
            }
            for student in students
        ]


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
        fields = ['id', 'username', 'email', 'password', 'subject', 'class_teacher_of']

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already registered.')
        return email

    def validate_class_teacher_of(self, value):
        if value is not None and Teacher.objects.filter(class_teacher_of=value).exists():
            raise serializers.ValidationError(
                f'A class teacher is already assigned for standard {value}.'
            )
        return value

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
            'class_teacher_of': instance.class_teacher_of,
        }
