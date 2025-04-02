from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, permissions



from learning_system.sending_email.send_email import generate_otp, sending_emails
from .models import Assignment, Course, CourseResource, User, OTP
from .serializers import (
    AssignmentSerializer, CourseResourceSerializer, CourseSerializer, UserSerializer, LoginSerializer, OTPVerificationSerializer, PasswordResetRequestSerializer, PasswordResetSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(**serializer.validated_data)
        user.is_active = False  
        user.save()

        OTP.objects.filter(user=user).delete()
        otp_instance = OTP.objects.create(user=user, code=generate_otp(), type=OTP.EMAIL_VALIDATION)

        sending_emails(send_to=user.email, body=f'Your OTP code is: {otp_instance.code}', sub="Registration")

        return Response({
            "message": "User registered successfully. Please verify OTP sent to your email."
        }, status=status.HTTP_201_CREATED)







class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        otp_code = serializer.validated_data.get("otp")

        try:
            user = User.objects.get(email=email)
            otp_instance = OTP.objects.get(user=user, code=otp_code, type=OTP.EMAIL_VALIDATION)

            if not otp_instance.is_valid():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            otp_instance.delete()

            return Response({
                "message": "OTP verified successfully!",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")

        try:
            user = User.objects.get(email=email)
            OTP.objects.filter(user=user, type=OTP.PASSWORD_RESET).delete()
            otp_instance = OTP.objects.create(user=user, code=generate_otp(), type=OTP.PASSWORD_RESET)

            sending_emails(send_to=email, body=f'Your OTP for password reset is: {otp_instance.code}', sub="Password Reset")

            return Response({"message": "OTP sent for password reset."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        otp_code = serializer.validated_data.get("otp")
        new_password = serializer.validated_data.get("new_password")

        try:
            user = User.objects.get(email=email)
            otp_instance = OTP.objects.get(user=user, code=otp_code, type=OTP.PASSWORD_RESET)

            if not otp_instance.is_valid():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            otp_instance.delete()

            return Response({"message": "Password reset successfully!"}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, OTP.DoesNotExist):
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "role": user.role if hasattr(user, "role") else "user",  # Ensure role is included
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
          
            OTP.objects.filter(user=user, type=OTP.EMAIL_VALIDATION).delete()

            otp_instance = OTP.objects.create(user=user, code=generate_otp(), type=OTP.EMAIL_VALIDATION)

            sending_emails(send_to=user.email, body=f'Your new OTP code is: {otp_instance.code}', sub="Resend OTP")

            return Response({"message": "New OTP has been sent to your email."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)




class HomepageCoursesView(ListAPIView):
    queryset = Course.objects.all()[:3]
    serializer_class = CourseSerializer



    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 
    
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

class CourseResourceViewSet(viewsets.ModelViewSet):
    queryset = CourseResource.objects.all()
    serializer_class = CourseResourceSerializer

