from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseResourceViewSet,
    HomepageCoursesView,
    ResendOTPView, 
    UserRegistrationView, 
    LoginView, 
    OTPVerificationView, 
    PasswordResetRequestView, 
    PasswordResetView, 
    CourseViewSet,
    AssignmentViewSet  # Import the new Assignment ViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'course-resources', CourseResourceViewSet)


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verifyotp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('request-password-reset/', PasswordResetRequestView.as_view(), name='request_password_reset'),
    path('reset-password/', PasswordResetView.as_view(), name='reset_password'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('courses/homepage/', HomepageCoursesView.as_view(), name='homepage_courses'),


    path('', include(router.urls)),
]
