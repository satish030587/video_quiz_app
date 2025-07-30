from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'questions', views.QuestionViewSet)
router.register(r'attempts', views.QuizAttemptViewSet, basename='attempts')

urlpatterns = [
    path('', include(router.urls)),
]