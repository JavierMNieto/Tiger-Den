from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

# Register your models here.
# How models appear in database (fields shown in edit page and in inlines inside other models)

from . import models

class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">Edit</a>'.format(u=url))
        else:
            return ''

class GroupOrderInline(EditLinkToInlineObject, admin.TabularInline):
    model = models.GroupOrder
    extra = 0
    fields = ["edit_link", "user", "location", "confirmed", "formatted_total", "created_at"]
    readonly_fields = ("edit_link", "user", "location", "confirmed", "formatted_total", "created_at")

class OrderInline(EditLinkToInlineObject, admin.TabularInline):
    model = models.Order
    extra = 0
    fields = ["edit_link", "name", "accepted", "formatted_total"]
    readonly_fields = ("edit_link", "name", "accepted", "formatted_total")

class ItemOrderInline2(EditLinkToInlineObject, admin.TabularInline):
    model = models.ItemOrder
    extra = 0
    fields = ["edit_link", "item", "quantity", "formatted_total"]
    readonly_fields = ("edit_link", "item", "quantity", "formatted_total")

class ItemOrderInline1(EditLinkToInlineObject, admin.TabularInline):
    model = models.ItemOrder
    extra = 0
    fields = ["edit_link", "order", "quantity", "formatted_total"]
    readonly_fields = ("edit_link", "order", "quantity", "formatted_total")

class GroupOrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "location", "confirmed", "formatted_total", "created_at")
    fields       = ["id", "user", "location", "confirmed", "formatted_total", "created_at"]
    readonly_fields = ("id", "formatted_total", "created_at")
    inlines = (OrderInline, )

class OrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "group", "accepted", "formatted_total")
    fields       = ["id", "name", "group", "accepted", "formatted_total"]
    readonly_fields = ("id", "formatted_total")
    inlines = (ItemOrderInline2, )

class ItemOrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "item", "quantity", "formatted_total")
    fields       = ["id", "item", "quantity", "formatted_total"]
    readonly_fields = ("id", "formatted_total")

class ItemAdmin(admin.ModelAdmin):
    #fields = ["image_tag", "image", "name", "description", "limited_time"]
    #readonly_fields = ("image_tag", )
    fields = ["name", "description", "limited_time"]
    inlines = (ItemOrderInline1, )

admin.site.register(models.GroupOrder, GroupOrderAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.ItemOrder, ItemOrderAdmin)
admin.site.register(models.Item, ItemAdmin)