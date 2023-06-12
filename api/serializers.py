from django.contrib.auth import password_validation
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.models import (
    Category,
    Contact,
    Order,
    OrderItem,
    Product,
    ProductInfo,
    ProductParameter,
    Shop,
    User,
)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        """ContactSerializer Meta."""

        model = Contact
        fields = (
            'id',
            'city',
            'street',
            'house',
            'structure',
            'building',
            'apartment',
            'user',
            'phone',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'user': {'write_only': True}}

class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    first_name = serializers.CharField(validators=[UnicodeUsernameValidator()])
    last_name = serializers.CharField(validators=[UnicodeUsernameValidator()])

    class Meta:
        """UserSerializer Meta."""

        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'company',
            'position',
            'contacts',
        )
        read_only_fields = ('id',)


class UserCreateSerializer(UserSerializer):
    password = serializers.CharField(
        validators=[password_validation.validate_password]
    )

    class Meta:
        """UserSerializer Meta."""

        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'password',
            'email',
            'company',
            'position',
            # 'contacts',
        )
        read_only_fields = ('id',)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        validators=[password_validation.validate_password]
    )

    class Meta:
        """UserSerializer Meta."""

        model = User
        fields = ('id', 'password', 'email')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        """CategorySerializer Meta."""

        model = Category
        fields = (
            'id',
            'name',
        )
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        """ShopSerializer Meta."""

        model = Shop
        fields = (
            'id',
            'name',
            'state',
        )
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        """ProductSerializer Meta."""

        model = Product
        fields = (
            'name',
            'category',
        )


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        """ProductParameterSerializer Meta."""

        model = ProductParameter
        fields = (
            'parameter',
            'value',
        )


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        """ProductInfoSerializer Meta."""

        model = ProductInfo
        fields = (
            'id',
            'model',
            'product',
            'shop',
            'quantity',
            'price',
            'price_rrc',
            'product_parameters',
        )
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        """OrderItemSerializer Meta."""

        model = OrderItem
        fields = (
            'id',
            'product_info',
            'quantity',
            'order',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'order': {'write_only': True}}


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        """OrderSerializer Meta."""

        model = Order
        fields = (
            'id',
            'ordered_items',
            'state',
            'dt',
            'total_sum',
            'contact',
        )
        read_only_fields = ('id',)
