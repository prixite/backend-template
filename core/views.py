from rest_framework import permissions, status, viewsets
from rest_framework.authtoken import views as authtoken_views
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import COUNTRIES, User
from core.permissions import (
    IsDefaultUser,
    IsNotDefaultUser,
    SignupPermission,
    UserPermission,
)
from core.serializers import (
    EmptySerializer,
    SignupSerializer,
    UserAdminSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsNotDefaultUser,
        UserPermission,
    ]

    @action(
        detail=True,
        methods=['post'],
    )
    def send_link(self, request, *args, **kwargs):
        user = self.get_object()
        user.send_verification_email()
        return Response(status=200)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[SignupPermission],
    )
    def signup(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path=r'verify/(?P<code>\w+)',
    )
    def verify(self, request, *args, **kwargs):
        user = self.get_object()
        code = kwargs['code']
        user.verify_email(code)

        headers = self.get_success_headers(kwargs)
        return Response(
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser],
    )
    def admin(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_staff = True
        user.save()

        headers = self.get_success_headers(kwargs)
        return Response(
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def get_serializer_class(self):
        if self.action == 'signup':
            return SignupSerializer
        elif self.action in ['admin', 'send_link']:  # pragma: no cover  # noqa
            # This block is for swagger documentation. It will not be used by
            # the code. Hence, the no-cover.
            return EmptySerializer
        elif self.request.user.is_staff:
            return UserAdminSerializer
        else:
            return UserSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if self.action == 'verify':
            return queryset

        if not user.is_staff:
            queryset = queryset.filter(id=user.id)

        return queryset.order_by('-date_joined')


class ObtainAuthToken(authtoken_views.ObtainAuthToken):
    permission_classes = [IsDefaultUser]


class CountryViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        countries = []
        for code, name in sorted(COUNTRIES, key=lambda x: x[1]):
            countries.append(dict(
                code=code,
                name=name,
            ))

        return Response(countries)
