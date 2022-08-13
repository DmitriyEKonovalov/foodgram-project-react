from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.serializers.users_serializers import (
    SubscribeSerializer, UserWithRecipesSerializer
)
from .models import User
from .serializers import BaseUserSerializer


class CustomUserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    ACTIONS_SERIALIZERS = {
        'create': settings.SERIALIZERS.user_create,
        'list': BaseUserSerializer,
        'retrieve': BaseUserSerializer,
        'me': BaseUserSerializer,
        'subscribe': SubscribeSerializer,
        'subscriptions': UserWithRecipesSerializer,
        'set_password': settings.SERIALIZERS.set_password,

    }

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        return super().get_permissions()

    def get_serializer_class(self):
        return self.ACTIONS_SERIALIZERS.get(self.action)

    def get_object(self):
        return self.request.user

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(
                self.request, context
            ).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        subscribed = user.subscribed.values_list('author_id', flat=True)
        queryset = User.objects.filter(id__in=subscribed)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs['pk'])
        data = {
            'user_id': user.id,
            'author_id': author.id,
            'method': self.request.method
        }
        context = {'user': user}
        serializer = SubscribeSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        # CREATE
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # DELETE
        user.subscribed.filter(author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)