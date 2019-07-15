import redis
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import User, Notification
from user.permissions import (
    BudgetViewSetPermission
)
from user.serializers import (
    UserSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
    InviteUserSerializer,
    FirebaseTokenUserSerializer,
    NotificationSerializer,
)

REDIS_CLIENT = redis.Redis()


class ProfileViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    retrieve: Получить пользователя по его id
    create: Создать пользователя
    update: Изменить пользователя
    partial_update: Изменить пользователя (partial update)
    """

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, BudgetViewSetPermission)
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ['notifications']:
            return NotificationSerializer
        if self.action in ['invite_again']:
            return InviteUserSerializer
        if self.action in ['set_firebase_token']:
            return FirebaseTokenUserSerializer
        if self.action in ['create']:
            return CreateUserSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        return super().get_serializer_class()

    @action(methods=['post'], url_path='invite-again', url_name='invite-again', detail=True)
    def invite_again(self, request, *args, **kwargs):
        """Повторная отправка приглашения"""

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            budget = self.get_object()
            budget.init_invite(request.user)
            return Response(status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], url_path='set-firebase-token', url_name='set-firebase-token', detail=True)
    def set_firebase_token(self, request, *args, **kwargs):
        """Установка FirebaseToken пользователю"""

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='notifications', url_name='notifications', detail=True)
    def notifications(self, request, *args, **kwargs):
        """
        get: Уведомления
        ---

        Тексты шаблонов уведомлений правятся в админке

        ## Пагинация
        * **page** - **__int__** - номер страницы
        * **size** - **__int__** - размер страницы

        ## Данные ответа
        * **id** - **__int__** - id уведомления
        * **user** - **__obj__** - объект юзера
        * **created** - **__date__** - дата записи уведомления "2019-07-09T03:52:28.901528+03:00"
        * **massage** - **__list__** - объект уведомления

            (
                'massage',
                [
                    'Заголовок',
                    'Тело сообщения'
                ]
            )

        """

        user = self.get_object()

        notifications = Notification.objects.filter(
            user=user
        )
        REDIS_CLIENT.set(f'messages_{user.id}', notifications.count())

        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)

    @action(methods=['get'], url_path='new-notifications', url_name='new-notifications', detail=True)
    def new_notifications_count(self, request, *args, **kwargs):
        """
        get: Количество непрочитаных уведомлений о событиях с заданием
        ---

        ## Ответ

            {'new_messages': 4}

        """

        user = self.get_object()

        notification_count = Notification.objects.filter(user=user).count()

        messages_count = REDIS_CLIENT.get(f'messages_{user.id}') or 0
        messages_count = notification_count - int(messages_count)
        REDIS_CLIENT.set(f'messages_{user.id}', messages_count if messages_count > 0 else notification_count)

        return Response(data={'new_messages': messages_count if messages_count > 0 else 0})
