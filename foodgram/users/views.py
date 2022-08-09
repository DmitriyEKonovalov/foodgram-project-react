import uuid
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import viewsets
from rest_framework import filters, mixins, permissions
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, update_session_auth_hash
from rest_framework import generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.db.models import Prefetch

from djoser import signals, utils
from djoser.compat import get_user_email
from djoser.conf import settings
from djoser.views import UserViewSet
from api.serializers.users_serializers import SubscribeSerializer
from api.serializers.users_serializers import UserWithRecipesSerializer
from .models import User
from .serializers import BaseUserSerializer


class CustomUserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()

    ACTIONS_SERIALIZERS = {
        'create': settings.SERIALIZERS.user_create,
        'list': BaseUserSerializer,
        'retrieve': BaseUserSerializer,
        'me': BaseUserSerializer,
        'subscribe': SubscribeSerializer,
        'set_password': settings.SERIALIZERS.set_password,

    }
    """
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset
    """

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        return super().get_permissions()

    def get_serializer_class(self):
        serializer_class = self.ACTIONS_SERIALIZERS.get(self.action)
        if serializer_class:
            return serializer_class
        return self.serializer_class

    # def get_instance(self):
    #     return self.request.user

    def get_object(self):
        return self.request.user

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

        """
        return super().set_password()

    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        user = request.user
        subscribed = user.subscribed.values_list('author_id', flat=True).all()
        queryset = User.objects.filter(id__in=subscribed).all()

        # pages = self.paginate_queryset(queryset)
        serializer = UserWithRecipesSerializer(
            queryset,
            # pages,
            many=True,
            context={'request': request}
        )
        # return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs['pk'])
        subscribe = user.subscribed.filter(author=author)
        data = {
            'user': user,
            'author': author
        }
        context = {'request': request, 'user': user, 'author': author}
        serializer = SubscribeSerializer(data=data, context=context)

        if request.method == 'POST' and serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        if serializer.is_valid(raise_exception=True):
            subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


