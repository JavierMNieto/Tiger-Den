from django.contrib import admin

from oscar.core.loading import get_model

Order = get_model('order', 'Order')
GroupOrder = get_model('order', 'GroupOrder')

class OrderInline(admin.TabularInline):
    model = Order
    extra = 0

class GroupOrderAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', ]
    list_display = ('number', 'total_excl_tax', 'user', 'date_placed', 'currency')
    readonly_fields = ('number', 'total_excl_tax', 'currency')
    inlines = [OrderInline]

admin.site.register(GroupOrder, GroupOrderAdmin)

from oscar.apps.order.admin import *  # noqa