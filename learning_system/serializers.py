from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from .models import OTP, Assignment, Course, CourseResource, User



class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=User.UserRoleChoices.choices)


    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_password(self, value):
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long, include at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return value



class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'image', 'title', 'description', 'created_at']
class AssignmentSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())  # ✅ Accepts course ID

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'available_date', 'due_date', 'points', 'course']
class CourseResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseResource
        fields = ['id', 'course', 'resource_type', 'title', 'url', 'file', 'created_at']

    def validate(self, data):
        resource_type = data.get("resource_type")
        url = data.get("url")
        file = data.get("file")

        # Check for valid resource type
        if resource_type not in dict(CourseResource.RESOURCE_TYPE_CHOICES):
            raise serializers.ValidationError({"resource_type": "Invalid resource type."})

        # Validate based on resource type
        if resource_type == "video":
            if not url:
                raise serializers.ValidationError({"url": "A video resource must have a URL."})
            if file:
                raise serializers.ValidationError({"error": "A video resource cannot have a file."})
        
        elif resource_type == "link":
            if not url:
                raise serializers.ValidationError({"url": "A link resource must have a URL."})
            if file:
                raise serializers.ValidationError({"error": "A link resource cannot have a file."})
        
        elif resource_type == "file":
            if not file:
                raise serializers.ValidationError({"file": "A file resource must have a file."})
            if url:
                raise serializers.ValidationError({"error": "A file resource cannot have a URL."})

        return data
    

