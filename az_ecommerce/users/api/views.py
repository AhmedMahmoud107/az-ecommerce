from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from az_ecommerce.users.api.serializers import ChangePassSerializer
from az_ecommerce.users.api.serializers import RestPasswordSerializer
from az_ecommerce.users.api.serializers import UserRegisterSerializer
from az_ecommerce.users.api.serializers import UserSerializer
from az_ecommerce.users.api.serializers import VerifyEmailSerializer
from az_ecommerce.users.models import User


class UserViewSet(ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)


class UserAuthViewSet(GenericViewSet):
    queryset = User.objects.all()

    @action(
        detail=False,
        methods=["post"],
        serializer_class=UserRegisterSerializer,
        permission_classes=[AllowAny],
    )
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    @action(
        detail=False,
        methods=["post"],
        serializer_class=ChangePassSerializer,
        permission_classes=[IsAuthenticated],
        url_path="change-pass",
    )
    def change_pass(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"password": "Password changed successfully"})

    @action(
        detail=False,
        methods=["post"],
        serializer_class=RestPasswordSerializer,
        permission_classes=[IsAuthenticated],
        url_path="reset-pass",
    )
    def reset_pass(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "check your mail for the link"},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        serializer_class=VerifyEmailSerializer,
        permission_classes=[AllowAny],
        url_path="verify-email",
    )
    def verify_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "check your mail for the link"},
            status=status.HTTP_200_OK,
        )
