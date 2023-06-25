
from django.contrib import admin
from django.urls import include, path, re_path
from django_rest_passwordreset.views import (
    reset_password_confirm,
    reset_password_request_token,
)
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from api.views import (
    AccountDetails,
    BasketView,
    CategoryView,
    ConfirmAccount,
    ContactView,
    LoginAccount,
    OrderView,
    PartnerOrders,
    PartnerState,
    PartnerUpdate,
    ProductInfoView,
    RegisterAccount,
    ShopView,
)

router = DefaultRouter()
router.register(r'user/contact', ContactView, basename='user-contact')
router.register(r'user', AccountDetails, basename='user-details')

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Netology diploma",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('', include(router.urls)),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path(
        'user/register/confirm',
        ConfirmAccount.as_view(),
        name='user-register-confirm',
    ),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path(
        'user/password_reset',
        reset_password_request_token,
        name='password-reset',
    ),
    path(
        'user/password_reset/confirm',
        reset_password_confirm,
        name='password-reset-confirm',
    ),
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('products', ProductInfoView.as_view(), name='products'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),
    path('admin/', admin.site.urls),
    # re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    # re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    # re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
   path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
