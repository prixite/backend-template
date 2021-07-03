import debug_toolbar
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from core import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('countries', views.CountryViewSet, basename='countries')

urlpatterns = [
    path('login/', views.ObtainAuthToken.as_view()),
    path('', include(router.urls)),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework'),
    ),
    path('admin/', admin.site.urls),
    path('openapi/', get_schema_view(
        title="Soccer Fantasy League",
        description="Backend Template For DRF",
        version="1.0.0"
    ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='docs/swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='docs'),
    path('__debug__/', include(debug_toolbar.urls)),
]
