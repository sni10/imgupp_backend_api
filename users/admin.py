from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription
from django.db import models

# Настройка отображения для модели SubscriptionPlan
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price')  # Какие поля показывать в списке
    search_fields = ('name',)  # Поля, по которым можно осуществлять поиск
    # formfield_overrides = {
    #     models.DurationField: {'widget': DurationSelectWidget},
    # }

# Настройка отображения для модели UserSubscription
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date')
    list_filter = ('plan', 'start_date')  # Фильтры для удобства навигации
    search_fields = ('user__username', 'plan__name')  # Поиск по имени пользователя и названию плана


# Регистрация моделей с настройками отображения
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(UserSubscription, UserSubscriptionAdmin)




