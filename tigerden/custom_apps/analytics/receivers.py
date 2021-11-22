from oscar.apps.analytics.receivers import _record_products_in_order, _record_user_order, logger
from oscar.core.loading import get_model
UserRecord = get_model('analytics', 'UserRecord')


def _record_user_order(user, order):
    try:
        record = UserRecord.objects.filter(user=user)
        affected = record.update(
            num_orders=F('num_orders') + 1,
            num_order_lines=F('num_order_lines') + order.num_lines,
            num_order_items=F('num_order_items') + order.num_items,
            total_spent=F('total_spent') + order.total_incl_tax,
            date_last_order=order.date_placed)
        if not affected:
            UserRecord.objects.create(
                user=user, num_orders=1, num_order_lines=order.num_lines,
                num_order_items=order.num_items,
                total_spent=order.total_incl_tax,
                date_last_order=order.date_placed)
    except IntegrityError:      # pragma: no cover
        logger.error(
            "IntegrityError in analytics when recording a user order.")


@receiver(order_placed)
def receive_order_placed(sender, order, user, **kwargs):
    if kwargs.get('raw', False):
        return
    _record_products_in_order(order)
    if user and user.is_authenticated:
        _record_user_order(user, order)
