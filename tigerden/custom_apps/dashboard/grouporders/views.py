from oscar.apps.dashboard.orders.views import OrderListView as GroupOrderListView, OrderDetailView as GroupOrderDetailView, OrderStatsView as GroupOrderStatsView
from oscar.core.loading import get_class, get_model

GroupOrder = get_model('grouporder', 'GroupOrder')

class GroupOrderListView(GroupOrderListView):
    """
    Dashboard view of all group orders
    """
    model = GroupOrder

class GroupOrderStatsView(GroupOrderStatsView):
    """
    Dashboard view for group order statistics
    """
    pass

class GroupOrderDetailView(GroupOrderDetailView):
    """
    Dashboard view of group order
    """
    pass