from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
# from rest_framework.routers import DefaultRouter

from backend.views import PartnerUpdate, RegisterAccount, LoginAccount, CategoryView, ShopView, ProductInfoView, \
    BasketView, \
    AccountDetails, ContactView, OrderView, PartnerState, PartnerOrders, ConfirmAccount

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.urls import path
from rest_framework import permissions



schema_view = get_schema_view(
   openapi.Info(
      title="API", 
      default_version='v1',
      description="Test API",  
      terms_of_service="https://www.google.com/policies/terms/",  
      contact=openapi.Contact(email="test@gmail.com"),  
      license=openapi.License(name="Название лицензии"),  
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


app_name = 'backend'
urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/details', AccountDetails.as_view(), name='user-details'),
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    path('categories', CategoryView.as_view(), name='categories'),
    path('shops', ShopView.as_view(), name='shops'),
    path('products', ProductInfoView.as_view(), name='products'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),

] 

