from django.contrib import admin
from .models import Client, UserActivity, PaymentIdentification
from import_export.admin import ImportExportModelAdmin


class UserActivityInline(admin.StackedInline):
    model = UserActivity
    can_delete = False
    verbose_name_plural = 'User Activity'
    fk_name = 'user'
    fieldsets = (
        ('Login Information', {
            'fields': ('last_login', 'last_logout', 'login_count')
        }),
        ('Security', {
            'fields': ('failed_login_attempts', 'last_failed_login', 'is_locked_out', 'lockout_time')
        }),
    )
    readonly_fields = (
    'last_login', 'last_logout', 'login_count', 'failed_login_attempts', 'last_failed_login', 'is_locked_out',
    'lockout_time')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'first_name', 'last_name', 'is_active'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_login', 'last_logout', 'login_count', 'failed_login_attempts', 'is_locked_out')
    list_filter = ('is_locked_out',)
    search_fields = ('user__username',)
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Login Information', {
            'fields': ('last_login', 'last_logout', 'login_count')
        }),
        ('Security', {
            'fields': ('failed_login_attempts', 'last_failed_login', 'is_locked_out', 'lockout_time')
        }),
    )
    readonly_fields = (
    'user', 'last_login', 'last_logout', 'login_count', 'failed_login_attempts', 'last_failed_login', 'is_locked_out',
    'lockout_time')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PaymentIdentification)
class PaymentIdentificationAdmin(ImportExportModelAdmin):
    list_display = ('description', 'money_in')
    search_fields = ('description', 'money_in')
    list_per_page = 10
