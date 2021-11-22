from django import template
from django.conf import settings
from datetime import datetime
from custom_apps.order.models import GroupOrder

register = template.Library()


@register.filter(name='add')
def add(a, b):
    return float(a) + float(b)


@register.filter(name='subtract')
def subtract(a, b):
    return float(a) - float(b)


@register.filter(name='order_by')
def order_by(queryset, order):
    return queryset.order_by(order)


@register.simple_tag(name='ongoing_group_orders')
def ongoing_group_orders():
    cnt = GroupOrder.objects.filter(status=settings.ONGOING_STATUS).count()
    per = min(1.0, cnt/settings.MAX_ONGOING_GROUP_ORDERS)

    status = 'Very Busy'
    css = 'danger'

    if per < 0.25:
        status = 'Quiet'
        css = 'success'
    elif per < 0.75:
        status = 'Busy'
        css = 'warning'

    return {
        'status': status,
        'css': css,
        'count': cnt,
        'percent': per*100
    }
