from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)

from . import views

app_name = 'weather_reminder'

router = routers.DefaultRouter()
router.register(r'subscriptions', views.SubscriptionView)

urlpatterns = [
    path('api/v1/users/register/', views.UserRegistrationView.as_view()),
    path('api/v1/', include(router.urls)),
    path('api/v1/cities/<int:pk>/', views.RetrieveCityView.as_view()),
    path('api/v1/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(),
         name='token_verify'),
]
