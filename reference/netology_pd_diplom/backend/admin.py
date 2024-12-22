from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ValidationError
from backend.tasks import do_import
from django.core.validators import URLValidator

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken


# Панель управления пользователями
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'type', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'type')
        

# Панель управления магазинами
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'user','id')
    search_fields = ('name', 'user__first_name', 'user__last_name')
    list_filter = ('state', 'name')
    list_editable = ('state',)
    ordering = ('name',)
    actions = ['start_import_task']
    def start_import_task(self, request, queryset):
        """
        Запускает Celery задачу для импорта товаров для выбранных магазинов.
        """
        validate_url = URLValidator()

        for shop in queryset:
            import_url = shop.import_url

            if import_url:git
                try:
                    validate_url(import_url) 
                    do_import.delay(shop.user.id, import_url)  
                    self.message_user(request, f"Импорт для магазина {shop.name} начат.")
                except ValidationError:
                    self.message_user(request, f"Неверный URL для магазина {shop.name}", level="error")
            else:
                self.message_user(request, f"Не указан URL для импорта товаров у магазина {shop.name}", level="error")

    start_import_task.short_description = "Запустить импорт товаров для выбранных магазинов"


# Встраиваемая модель для категорий
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1 

    
# Панель управления категориями   
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    inlines = [ProductInline]


# Панель управления продуктами
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)
    

# Встраиваемая модель для информации о продукте
class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1


# Панель управления информацией о продукте
@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc')
    search_fields = ('model', 'product__name')
    inlines = [ProductParameterInline,]


# Панель управления параметрами продукта
@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    search_fields = ('name',)


# Панель управления связями параметров с продуктами
@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info__product__name', 'parameter', 'value')
    search_fields = ('product_info__product__name', 'parameter__name') 
    list_filter = ('parameter', 'product_info__product__name')  


# Встраиваемая модель для заказов
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    

# Панель управления заказами
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'state','contact','dt', 'updated_dt', 'contact')
    list_filter = ('state',)
    inlines = [OrderItemInline,]


# Панель управления товарами в заказах
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info','product_info__product__name', 'quantity',)
    search_fields = ('order__id', 'product_info__product__name')
    list_filter = ('order',)


# Панель управления контактами
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
    search_fields = ('city', 'street')


# Панель управления токенами подтверждения email
@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
    search_fields = ('user__first_name', 'user__last_name', 'key')
    list_filter = ('created_at',)
    ordering = ('created_at',)