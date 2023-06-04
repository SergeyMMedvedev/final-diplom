from distutils.util import strtobool

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import F, Q, Sum
from requests import get
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json
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
)
from api.serializers import (
    CategorySerializer,
    ContactSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductInfoSerializer,
    ShopSerializer,
    UserSerializer,
)
from api.signals import new_order, new_user_registered


class RegisterAccount(APIView):
    """Для регистрации покупателей."""

    def post(self, request, *args, **kwargs) -> Response:
        """Регистрация методом POST."""
        # проверяем обязательные аргументы
        if {
            'first_name',
            'last_name',
            'email',
            'password',
            'company',
            'position',
        }.issubset(request.data):
            # проверяем пароль на сложность

            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return Response({'Status': False, 'Errors': {'password': error_array}})
            else:
                # проверяем данные для уникальности имени пользователя
                # request.data._mutable = True
                request.data.update({})
                user_serializer = UserSerializer(data=request.data)
                if user_serializer.is_valid():
                    # сохраняем пользователя
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    new_user_registered.send(
                        sender=self.__class__, user_id=user.id
                    )
                    return Response({'Status': True})
                else:
                    return Response(
                        {'Status': False, 'Errors': user_serializer.errors}
                    )
        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, 
        )


class ConfirmAccount(APIView):
    """Класс для подтверждения почтового адреса."""

    def post(self, request, *args, **kwargs) -> Response:
        """Регистрация методом POST."""
        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(
                user__email=request.data['email'], key=request.data['token']
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
                    }
                )

        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )


class AccountDetails(APIView):
    """Класс для работы данными пользователя."""

    def get(self, request, *args, **kwargs) -> Response:
        """получить данные."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs) -> Response:
        """Редактирование методом POST."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )
        # проверяем обязательные аргументы

        if 'password' in request.data:
            # проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return Response(
                    {'Status': False, 'Errors': {'password': password_error}}
                )
            else:
                request.user.set_password(request.data['password'])

        # проверяем остальные данные
        user_serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'Status': True})
        else:
            return Response(
                {'Status': False, 'Errors': user_serializer.errors}
            )


class LoginAccount(APIView):
    """Класс для авторизации пользователей."""

    def post(self, request, *args, **kwargs) -> Response:
        """Авторизация методом POST."""
        if {'email', 'password'}.issubset(request.data):

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
                {'Status': False, 'Errors': 'Не удалось авторизовать'}
            )

        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )


class CategoryView(ListAPIView):
    """Класс для просмотра категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """Класс для просмотра списка магазинов."""

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductInfoView(APIView):
    """Класс для поиска товаров."""

    def get(self, request, *args, **kwargs) -> Response:
        """Get products."""
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        # фильтруем и отбрасываем дуликаты
        queryset = (
            ProductInfo.objects.filter(query)
            .select_related('shop', 'product__category')
            .prefetch_related('product_parameters__parameter')
            .distinct()
        )

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    """Класс для работы с корзиной пользователя."""

    def get(self, request, *args, **kwargs) -> Response:
        """получить корзину."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )
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
                )
            )
            .distinct()
        )

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs) -> Response:
        """редактировать корзину."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return Response(
                    {'Status': False, 'Errors': 'Неверный формат запроса'}
                )
            else:
                basket, _ = Order.objects.get_or_create(
                    user_id=request.user.id, state='basket'
                )
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': basket.pk})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return Response(
                                {'Status': False, 'Errors': str(error)}
                            )
                        else:
                            objects_created += 1

                    else:
                        return Response(
                            {'Status': False, 'Errors': serializer.errors}
                        )

                return Response(
                    {'Status': True, 'Создано объектов': objects_created}
                )
        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )

    def delete(self, request, *args, **kwargs) -> Response:
        """удалить товары из корзины."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(
                user_id=request.user.id, state='basket'
            )
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
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
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return Response(
                    {'Status': False, 'Errors': 'Неверный формат запроса'}
                )
            else:
                basket, _ = Order.objects.get_or_create(
                    user_id=request.user.id, state='basket'
                )
                objects_updated = 0
                for order_item in items_dict:
                    if (
                        type(order_item['id']) == int
                        and type(order_item['quantity']) == int
                    ):
                        objects_updated += OrderItem.objects.filter(
                            order_id=basket.pk, id=order_item['id']
                        ).update(quantity=order_item['quantity'])

                return Response(
                    {'Status': True, 'Обновлено объектов': objects_updated}
                )
        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )


class PartnerUpdate(APIView):
    """Класс для обновления прайса от поставщика."""

    def post(self, request, *args, **kwargs) -> Response:
        """Create price."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )
        print(request.user)
        if request.user.type != 'shop':  # type: ignore
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'}, status=403
            )

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


class PartnerState(APIView):
    """Класс для работы со статусом поставщика."""

    def get(self, request, *args, **kwargs) -> Response:
        """получить текущий статус."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        if request.user.type != 'shop':
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'}, status=403
            )

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs) -> Response:
        """изменить текущий статус."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        if request.user.type != 'shop':
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'}, status=403
            )
        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id).update(
                    state=strtobool(state)
                )
                return Response({'Status': True})
            except ValueError as error:
                return Response({'Status': False, 'Errors': str(error)})

        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )


class PartnerOrders(APIView):
    """Класс для получения заказов поставщиками."""

    def get(self, request, *args, **kwargs) -> Response:
        """Get PartnerOrders."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        if request.user.type != 'shop':
            return Response(
                {'Status': False, 'Error': 'Только для магазинов'}, status=403
            )

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

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class ContactView(APIView):
    """Класс для работы с контактами покупателей."""

    def get(self, request, *args, **kwargs) -> Response:
        """получить мои контакты."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs) -> Response:
        """добавить новый контакт."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        if {'city', 'street', 'phone'}.issubset(request.data):
            request.data._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({'Status': True})
            else:
                return Response(
                    {'Status': False, 'Errors': serializer.errors}
                )

        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )

    def delete(self, request, *args, **kwargs) -> Response:
        """удалить контакт."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            query = Q()
            objects_deleted = False
            for contact_id in items_list:
                if contact_id.isdigit():
                    query = query | Q(user_id=request.user.id, id=contact_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = Contact.objects.filter(query).delete()[0]
                return Response(
                    {'Status': True, 'Удалено объектов': deleted_count}
                )
        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )

    def put(self, request, *args, **kwargs) -> Response:
        """редактировать контакт."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        if 'id' in request.data:
            if request.data['id'].isdigit():
                contact = Contact.objects.filter(
                    id=request.data['id'], user_id=request.user.id
                ).first()
                print(contact)
                if contact:
                    serializer = ContactSerializer(
                        contact, data=request.data, partial=True
                    )
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'Status': True})
                    else:
                        return Response(
                            {'Status': False, 'Errors': serializer.errors}
                        )

        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )


class OrderView(APIView):
    """Класс для получения и размешения заказов пользователями."""

    def get(self, request, *args, **kwargs) -> Response:
        """получить мои заказы."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )
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

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs) -> Response:
        """разместить заказ из корзины."""
        if not request.user.is_authenticated:
            return Response(
                {'Status': False, 'Error': 'Log in required'}, status=403
            )

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']
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
                        new_order.send(
                            sender=self.__class__, user_id=request.user.id
                        )
                        return Response({'Status': True})

        return Response(
            {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}
        )
