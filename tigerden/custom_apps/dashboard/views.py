from oscar.apps.dashboard.views import IndexView as CustomIndexView
from datetime import timedelta
from django.utils.timezone import now
from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_model
from django.db.models import Avg, Count, Sum
from decimal import Decimal as D
from decimal import ROUND_UP
from django.conf import settings

ConditionalOffer = get_model('offer', 'ConditionalOffer')
Voucher = get_model('voucher', 'Voucher')
Basket = get_model('basket', 'Basket')
StockAlert = get_model('partner', 'StockAlert')
Product = get_model('catalogue', 'Product')
Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
User = get_user_model()

class IndexView(CustomIndexView):
    def get_hourly_report(self, orders, hours=24, segments=10):
        """
        Get report of order revenue split up in hourly chunks. A report is
        generated for the last *hours* (default=24) from the current time.
        The report provides ``max_revenue`` of the hourly order revenue sum,
        ``y-range`` as the labelling for the y-axis in a template and
        ``order_total_hourly``, a list of properties for hourly chunks.
        *segments* defines the number of labelling segments used for the y-axis
        when generating the y-axis labels (default=10).
        """
        # Get datetime for 24 hours ago
        time_now = now().replace(minute=0, second=0)
        start_time = time_now - timedelta(hours=hours - 1)

        order_total_hourly = []
        for hour in range(0, hours, 2):
            end_time = start_time + timedelta(hours=2)
            hourly_orders = orders.filter(date_placed__gte=start_time,
                                          date_placed__lt=end_time).exclude(status__exact=next(iter(getattr(settings, 'OSCAR_ORDER_STATUS_PIPELINE', {}))))
            total = hourly_orders.aggregate(
                Sum('total_incl_tax')
            )['total_incl_tax__sum'] or D('0.0')
            order_total_hourly.append({
                'end_time': end_time,
                'total_incl_tax': total
            })
            start_time = end_time

        max_value = max([x['total_incl_tax'] for x in order_total_hourly])
        divisor = 1
        while divisor < max_value / 50:
            divisor *= 10
        max_value = (max_value / divisor).quantize(D('1'), rounding=ROUND_UP)
        max_value *= divisor
        if max_value:
            segment_size = (max_value) / D('100.0')
            for item in order_total_hourly:
                item['percentage'] = int(item['total_incl_tax'] / segment_size)

            y_range = []
            y_axis_steps = max_value / D(str(segments))
            for idx in reversed(range(segments + 1)):
                y_range.append(idx * y_axis_steps)
        else:
            y_range = []
            for item in order_total_hourly:
                item['percentage'] = 0

        ctx = {
            'order_total_hourly': order_total_hourly,
            'max_revenue': max_value,
            'y_range': y_range,
        }
        return ctx

    def get_stats(self):
        datetime_24hrs_ago = now() - timedelta(hours=24)

        # Only get orders passed first status        
        orders = Order.objects.all().exclude(status__exact=next(iter(getattr(settings, 'OSCAR_ORDER_STATUS_PIPELINE', {}))))
        alerts = StockAlert.objects.all()
        baskets = Basket.objects.filter(status=Basket.OPEN)
        customers = User.objects.filter(orders__isnull=False).distinct()
        lines = Line.objects.filter()
        products = Product.objects.all()

        user = self.request.user
        if not user.is_staff:
            partners_ids = tuple(user.partners.values_list('id', flat=True))
            orders = orders.filter(
                lines__partner_id__in=partners_ids
            ).distinct()
            alerts = alerts.filter(stockrecord__partner_id__in=partners_ids)
            baskets = baskets.filter(
                lines__stockrecord__partner_id__in=partners_ids
            ).distinct()
            customers = customers.filter(
                orders__lines__partner_id__in=partners_ids
            ).distinct()
            lines = lines.filter(partner_id__in=partners_ids)
            products = products.filter(stockrecords__partner_id__in=partners_ids)

        orders_last_day = orders.filter(date_placed__gt=datetime_24hrs_ago)
        open_alerts = alerts.filter(status=StockAlert.OPEN)
        closed_alerts = alerts.filter(status=StockAlert.CLOSED)

        total_lines_last_day = lines.filter(order__in=orders_last_day).count()
        stats = {
            'total_orders_last_day': orders_last_day.count(),
            'total_lines_last_day': total_lines_last_day,

            'average_order_costs': orders_last_day.aggregate(
                Avg('total_incl_tax')
            )['total_incl_tax__avg'] or D('0.00'),

            'total_revenue_last_day': orders_last_day.aggregate(
                Sum('total_incl_tax')
            )['total_incl_tax__sum'] or D('0.00'),

            'hourly_report_dict': self.get_hourly_report(orders),
            'total_customers_last_day': customers.filter(
                date_joined__gt=datetime_24hrs_ago,
            ).count(),

            'total_open_baskets_last_day': baskets.filter(
                date_created__gt=datetime_24hrs_ago
            ).count(),

            'total_products': products.count(),
            'total_open_stock_alerts': open_alerts.count(),
            'total_closed_stock_alerts': closed_alerts.count(),

            'total_customers': customers.count(),
            'total_open_baskets': baskets.count(),
            'total_orders': orders.count(),
            'total_lines': lines.count(),
            'total_revenue': orders.aggregate(
                Sum('total_incl_tax')
            )['total_incl_tax__sum'] or D('0.00'),

            'order_status_breakdown': orders.order_by(
                'status'
            ).values('status').annotate(freq=Count('id'))
        }
        if user.is_staff:
            stats.update(
                total_site_offers=self.get_active_site_offers().count(),
                total_vouchers=self.get_active_vouchers().count(),
            )
        return stats