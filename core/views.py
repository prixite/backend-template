from django.db.models import Sum
from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken import views as authtoken_views
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.lib import generate_team
from core.models import COUNTRIES, Player, Team, Transfer, User
from core.permissions import (
    IsAdminOrReadonly,
    IsDefaultUser,
    IsNotDefaultUser,
    PlayerPermission,
    SignupPermission,
    TeamPermission,
    UserPermission,
)
from core.serializers import (
    AddPlayerToTeamSerializer,
    EmptySerializer,
    PlayerAdminSerializer,
    PlayerBuySerializer,
    PlayerSellSerializer,
    PlayerSerializer,
    SignupSerializer,
    TeamAdminSerializer,
    TeamSerializer,
    TransferSerializer,
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

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser],
    )
    def generate(self, request, *args, **kwargs):
        user = self.get_object()
        generate_team(user)

        headers = self.get_success_headers(kwargs)
        return Response(
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def get_serializer_class(self):
        if self.action == 'signup':
            return SignupSerializer
        elif self.action in ['admin', 'generate', 'send_link']:  # pragma: no cover  # noqa
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


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    permission_classes = [
        IsNotDefaultUser,
        TeamPermission,
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if not user.is_staff:
            queryset = queryset.filter(owner=user)

        return queryset.order_by('name')

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return TeamAdminSerializer

        return TeamSerializer

    @method_decorator(cache_page(30))
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def rank(self, request, *args, **kwargs):
        teams = Team.objects
        teams = teams.annotate(market_value=Sum('players__market_value'))
        teams = teams.order_by('-market_value')[:10]
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    permission_classes = [IsNotDefaultUser, PlayerPermission]

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsNotDefaultUser, permissions.IsAuthenticated]
    )
    def sell(self, request, *args, **kwargs):
        player = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player.sell(serializer.data['fee'])
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsNotDefaultUser, permissions.IsAuthenticated]
    )
    def buy(self, request, *args, **kwargs):
        player = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.validated_data['team']

        if team == player.team:
            self.permission_denied(request)

        if not (request.user.is_staff or team.owner == request.user):
            self.permission_denied(request)

        try:
            Player.buy(player, team)
        except IntegrityError:
            raise ValidationError()

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
    def move(self, request, *args, **kwargs):
        player = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.validated_data['team']

        player.team = team
        player.save()

        headers = self.get_success_headers(kwargs)
        return Response(
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def get_queryset(self):
        queryset = super().get_queryset()

        team_id = self.request.query_params.get('team_id')
        if team_id is not None:
            queryset = queryset.filter(team_id=team_id)

        user = self.request.user
        if user.is_staff or self.action == 'buy':
            qs = queryset
        else:
            try:
                qs = queryset.filter(team=user.team)
            except User.team.RelatedObjectDoesNotExist:
                qs = queryset.none()

        return qs.order_by('first_name')

    def get_serializer_class(self):

        if self.action == 'buy':
            return PlayerBuySerializer

        if self.action == 'sell':
            return PlayerSellSerializer

        if self.action == 'move':
            return AddPlayerToTeamSerializer

        if self.request.user.is_staff:
            return PlayerAdminSerializer

        return PlayerSerializer


class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsNotDefaultUser,
        IsAdminOrReadonly,
    ]

    def get_queryset(self):
        queryset = Transfer.objects.all()

        country = self.request.query_params.get('country')
        if country is not None:
            queryset = queryset.filter(player__country=country.upper())

        first_name = self.request.query_params.get('first_name')
        if first_name is not None:
            queryset = queryset.filter(player__first_name__iexact=first_name)

        last_name = self.request.query_params.get('last_name')
        if last_name is not None:
            queryset = queryset.filter(player__last_name__iexact=last_name)

        team = self.request.query_params.get('team')
        if team is not None:
            queryset = queryset.filter(player__team__name__iexact=team)

        value = self.request.query_params.get('value')
        if value is not None:
            value = int(value)
            queryset = queryset.filter(fee=value)

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        return TransferSerializer


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
