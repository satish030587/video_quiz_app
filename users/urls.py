from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import views_certificate

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'progress', views.UserProgressViewSet, basename='progress')
router.register(r'certificates', views_certificate.CertificateViewSet, basename='certificates')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]