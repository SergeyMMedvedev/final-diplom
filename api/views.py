from distutils.util import strtobool

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import F, Q, Sum
from django.db.models.manager import BaseManager
from django.shortcuts import get_object_or_404
from requests import get
from rest_framework import mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
)
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from yaml import Loader
from yaml import load as load_yaml

from api.models import (
    Category,
    ConfirmEmailToken,
    Contact,
    Order,
    OrderItem,
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
    User,
)
from api.serializers import (
    CategorySerializer,
    ContactSerializer,
    OrderDelSerializer,
    OrderItemSerializer,
    OrderItemUpdSerializer,
    OrderSerializer,
    OrderUpdSerializer,
    ProductInfoSerializer,
    ShopSerializer,
    UserCreateSerializer,
    UserLoginSerializer,
    UserSerializer,
)
from api.signals import new_order, new_user_registered

from .permissions import IsAuthenticated, IsShopOwner


class RegisterAccount(CreateAPIView):
    """Для регистрации покупателей."""

    throttle_classes = [UserRateThrottle]
    serializer_class = UserCreateSerializer

    def post(self, request) -> Response:
        """Регистрация методом POST."""
        user_serializer = self.get_serializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(request.data['password'])
            user.save()
            new_user_registered.send(sender=self.__class__, user_id=user.id)
            return Response({'Status': True})
        else:
            return Response(
                {'Status': False, 'Errors': user_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ConfirmAccount(ListAPIView):
    """Класс для подтверждения почтового адреса."""

    throttle_classes = [UserRateThrottle]

    def get(self, request) -> Response:
        """Подтверждение регистрации по ссылке из почты."""
        confirmation_code = request.GET.get('token')
        email = request.GET.get('email')
        if not all([confirmation_code, email]):
            return Response(
                {
                    'Status': False,
                    'Errors': 'Не указаны все необходимые аргументы',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = ConfirmEmailToken.objects.filter(
            user__email=email, key=confirmation_code
        ).first()
        if token:
            token.user.is_active = True
            token.user.save()
            token.delete()
            return Response({'Status': True})
        else:
            return Response(
                {
                    'Status': False,
                    'Errors': 'Неправильно указан токен или email',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginAccount(CreateAPIView):
    """Класс для авторизации пользователей."""

    throttle_classes = [UserRateThrottle]
    serializer_class = UserLoginSerializer

    def post(self, request) -> Response:
        """Авторизация методом POST."""
        user_serializer = self.get_serializer(data=request.data)
        if not user_serializer.is_valid():
            return Response(
                {'Status': False, 'Errors': user_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(
            request,
            username=request.data['email'],
            password=request.data['password'],
        )
        if user is not None:
            if user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'Status': True, 'Token': token.key})

        return Response(
            {'Status': False, 'Errors': 'Не удалось авторизовать'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AccountDetails(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """Класс для получения или изменения пользовательских данных."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    throttle_classes = [UserRateThrottle]

    def get_object(self) -> User:
        """Возвращает пользователя, которого отображает представление."""
        user = get_object_or_404(
            self.queryset, username=self.kwargs.get('username')
        )
        return user

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def details(self, request, *args, **kwargs) -> Response:
        """Получить/изменить информацию о себе."""
        user = self.request.user
        if request.method == 'PATCH':
            kwargs['partial'] = True
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                user, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PartnerUpdate(CreateAPIView):
    """Класс для обновления прайса от поставщика."""

    permission_classes = [IsAuthenticated, IsShopOwner]  # noqa: F811
    throttle_classes = [UserRateThrottle]

    def post(self, request, *args, **kwargs) -> Response:
        """Create price."""
        url = request.data.get('url')  # type: ignore
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)
                shop, _ = Shop.objects.get_or_create(
                    name=data['shop'], user_id=request.user.pk
                )
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(
                        id=category['id'], name=category['name']
                    )
                    category_object.shops.add(shop.pk)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.pk).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(
                        name=item['name'], category_id=item['category']
                    )

                    product_info = ProductInfo.objects.create(
                        product_id=product.pk,
                        external_id=item['id'],
                        model=item['model'],
                        price=item['price'],
                        price_rrc=item['price_rrc'],
                        quantity=item['quantity'],
                        shop_id=shop.pk,
                    )
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(
                            name=name
                        )
                        ProductParameter.objects.create(
                            product_info_id=product_info.pk,
                            parameter_id=parameter_object.pk,
                            value=value,
                        )

                return Response({'Status': True})

        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )


class CategoryView(ListAPIView):
    """Класс для просмотра категорий."""

    throttle_classes = [UserRateThrottle]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """Класс для просмотра списка магазинов."""

    throttle_classes = [UserRateThrottle]

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductInfoView(ListAPIView):
    """Класс для поиска товаров."""

    throttle_classes = [UserRateThrottle]
    serializer_class = ProductInfoSerializer

    def get(self, request, *args, **kwargs) -> Response:
        """Получить товары."""
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        queryset = (
            ProductInfo.objects.filter(query)
            .select_related('shop', 'product__category')
            .prefetch_related('product_parameters__parameter')
            .distinct()
        )

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class ContactView(viewsets.ModelViewSet):
    """Класс для работы с контактами покупателей."""

    throttle_classes = [UserRateThrottle]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [
        IsAuthenticated,
    ]  # noqa: F811

    def get_queryset(self) -> BaseManager[Contact] | list:
        """Get queryset for current user."""
        if self.request.user.is_anonymous:
            return []
        lookups = Q(user=self.request.user)
        queryset = self.queryset.filter(lookups)
        return queryset

    def perform_create(self, serializer) -> None:
        """Set current user for create."""
        user = self.request.user
        serializer.save(user=user)

    def perform_update(self, serializer) -> None:
        """Set current user for upd."""
        user = self.request.user
        serializer.save(user=user)


class PartnerState(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsShopOwner]  # noqa: F811
    throttle_classes = [UserRateThrottle]
    serializer_class = ShopSerializer
    """Класс для работы со статусом поставщика."""

    def get(self, request, *args, **kwargs) -> Response:
        """Получить текущий статус."""
        shop = request.user.shop
        serializer = self.get_serializer(shop)
        return Response(serializer.data)

    def post(self, request) -> Response:
        """Изменить текущий статус."""
        state = request.data.get('state')
        data = {**request.data, "name": request.user.shop.name}
        if not isinstance(state, bool):
            data['state'] = strtobool(state)
        serializer = self.get_serializer(data=data)  # type: ignore
        if not serializer.is_valid():
            return Response(
                {'Status': False, 'Errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.update(instance=request.user.shop, validated_data=data)
        return Response({'Status': True})


class BasketView(GenericAPIView):
    """Класс для работы с корзиной пользователя."""

    permission_classes = [IsAuthenticated]  # noqa: F811
    throttle_classes = [UserRateThrottle]
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs) -> Response:
        """получить корзину."""
        basket = (
            Order.objects.filter(user_id=request.user.id, state='basket')
            .prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter',
            )
            .annotate(
                total_sum=Sum(
                    F('ordered_items__quantity')
                    * F('ordered_items__product_info__price')
                ),
            )
            .distinct()
            .first()
        )
        serializer = self.get_serializer(basket)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs) -> Response:
        """редактировать корзину."""
        basket, _ = Order.objects.get_or_create(
            user_id=request.user.id, state='basket'
        )
        for order_item in request.data:
            order_item.update({'order': basket.pk})
        serializer = OrderItemSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {'Status': False, 'Errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer.save()
        except IntegrityError as error:
            return Response({'Status': False, 'Errors': str(error)})
        return Response(
            {'Status': True, 'Создано объектов': len(request.data)}
        )

    def delete(self, request, *args, **kwargs) -> Response:
        """удалить товары из корзины."""
        serializer = OrderDelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'Status': False, 'Errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        basket, _ = Order.objects.get_or_create(
            user_id=request.user.id, state='basket'
        )
        query = Q()
        objects_deleted = False
        for order_item_id in request.data.get('ordered_items', []):
            query = query | Q(order_id=basket.pk, id=order_item_id)
            objects_deleted = True

        if objects_deleted:
            deleted_count = OrderItem.objects.filter(query).delete()[0]
            return Response(
                {'Status': True, 'Удалено объектов': deleted_count}
            )
        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )

    def put(self, request, *args, **kwargs) -> Response:
        """добавить позиции в корзину."""
        serializer = OrderItemUpdSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(
                {'Status': False, 'Errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        basket, _ = Order.objects.get_or_create(
            user_id=request.user.id, state='basket'
        )
        objects_updated = 0
        for order_item in request.data:
            objects_updated += OrderItem.objects.filter(
                order_id=basket.pk, id=order_item['id']
            ).update(quantity=order_item['quantity'])

        return Response(
            {'Status': True, 'Обновлено объектов': objects_updated}
        )


class PartnerOrders(ListAPIView):
    """Класс для получения заказов поставщиками."""

    permission_classes = [IsAuthenticated, IsShopOwner]  # noqa: F811
    throttle_classes = [UserRateThrottle]
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs) -> Response:
        """Get Partner Orders."""
        order = (
            Order.objects.filter(
                ordered_items__product_info__shop__user_id=request.user.id
            )
            .exclude(state='basket')
            .prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter',
            )
            .select_related('contact')
            .annotate(
                total_sum=Sum(
                    F('ordered_items__quantity')
                    * F('ordered_items__product_info__price')
                )
            )
            .distinct()
        )
        serializer = self.get_serializer(order, many=True)
        return Response(serializer.data)


class OrderView(ListCreateAPIView):
    """Класс для получения и размещения заказов пользователями."""

    permission_classes = [
        IsAuthenticated,
    ]  # noqa: F811
    throttle_classes = [UserRateThrottle]
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs) -> Response:
        """получить мои заказы."""
        order = (
            Order.objects.filter(user_id=request.user.id)
            .exclude(state='basket')
            .prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter',
            )
            .select_related('contact')
            .annotate(
                total_sum=Sum(
                    F('ordered_items__quantity')
                    * F('ordered_items__product_info__price')
                )
            )
            .distinct()
        )
        serializer = self.get_serializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs) -> Response:
        """разместить заказ из корзины."""
        serializer = OrderUpdSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'Status': False, 'Errors': serializer.errors})
        try:
            is_updated = Order.objects.filter(
                user_id=request.user.id, state='basket'
            ).update(contact_id=request.data['contact'], state='new')
        except IntegrityError as error:
            print(error)
            return Response(
                {
                    'Status': False,
                    'Errors': 'Неправильно указаны аргументы',
                }
            )
        else:
            if is_updated:
                new_order.send(sender=self.__class__, user_id=request.user.id)
                return Response({'Status': True})
        return Response({'Status': False})
