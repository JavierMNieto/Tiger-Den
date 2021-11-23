import datetime
from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.views.generic import DetailView, FormView, ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from oscar.core.compat import UnicodeCSVWriter
from oscar.apps.dashboard.orders import views
from oscar.core.loading import get_class, get_model
from oscar.core.utils import datetime_combine
from oscar.apps.order import exceptions as order_exceptions
from oscar.core.utils import datetime_combine, format_datetime
from oscar.views import sort_queryset

EventHandler = get_class('order.processing', 'EventHandler')
Order = get_model('order', 'Order')
GroupOrder = get_model('order', 'GroupOrder')

GroupOrderSearchForm = get_class(
    'dashboard.grouporders.forms', 'GroupOrderSearchForm')


def queryset_grouporders_for_user(user):
    """
    Returns a queryset of all group orders that a user is allowed to access.
    A staff user may access all group orders.
    """
    queryset = GroupOrder._default_manager.select_related(
        'user'
    ).prefetch_related('orders', 'status_changes')
    return queryset


def get_grouporder_for_user_or_404(user, number):
    try:
        return queryset_grouporders_for_user(user).get(number=number)
    except ObjectDoesNotExist:
        raise Http404()


class GroupOrderListView(views.OrderListView):
    model = GroupOrder
    context_object_name = 'grouporders'
    template_name = 'oscar/dashboard/grouporders/grouporder_list.html'
    form_class = GroupOrderSearchForm
    actions = ('download_selected_orders', 'change_grouporder_statuses',
               'change_grouporder_status', 'product_out_of_stock')
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        # base_queryset is equal to all orders the user is allowed to access
        self.base_queryset = queryset_grouporders_for_user(
            request.user).order_by('-date_placed')
        return ListView.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if 'order_number' in request.GET and request.GET.get(
                'response_format', 'html') == 'html':
            # Redirect to Order detail page if valid order number is given
            try:
                order = self.base_queryset.get(
                    number=request.GET['order_number'])
            except GroupOrder.DoesNotExist:
                pass
            else:
                return redirect(
                    'dashboard:grouporder-detail', number=order.number)

        if 'last_id' in request.GET:
            return self.update_grouporders(request)

        return ListView.get(self, request, *args, **kwargs)

    def get_queryset(self):  # noqa (too complex (19))
        """
        Build the queryset for this list.
        """
        queryset = sort_queryset(self.base_queryset, self.request,
                                 ['number', 'total_excl_tax'])

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if not self.request.GET:
            data['date_from'] = datetime.datetime.fromtimestamp(
                datetime.datetime.now().timestamp() - 36000)  # past 10 hours

        if data['order_number']:
            queryset = self.base_queryset.filter(
                number__istartswith=data['order_number'])

        if data['name']:
            # If the value is two words, then assume they are first name and
            # last name
            parts = data['name'].split()

            if len(parts) == 1:
                parts = [data['name'], data['name']]
            else:
                parts = [parts[0], parts[1:]]

            filter = Q(user__first_name__istartswith=parts[0])
            filter |= Q(user__last_name__istartswith=parts[1])

            queryset = queryset.filter(filter).distinct()

        """
        if data['product_title']:
            queryset = queryset.filter(
                lines__title__istartswith=data['product_title']).distinct()

        if data['upc']:
            queryset = queryset.filter(lines__upc=data['upc'])

        if data['partner_sku']:
            queryset = queryset.filter(lines__partner_sku=data['partner_sku'])

        if data['voucher']:
            queryset = queryset.filter(
                discounts__voucher_code=data['voucher']).distinct()
        """

        if data['date_from'] and data['date_to']:
            date_to = datetime_combine(data['date_to'], datetime.time.max)
            date_from = datetime_combine(data['date_from'], datetime.time.min)
            queryset = queryset.filter(
                date_placed__gte=date_from, date_placed__lt=date_to)
        elif data['date_from']:
            date_from = datetime_combine(data['date_from'], datetime.time.min)
            queryset = queryset.filter(date_placed__gte=date_from)
        elif data['date_to']:
            date_to = datetime_combine(data['date_to'], datetime.time.max)
            queryset = queryset.filter(date_placed__lt=date_to)

        if data['payment_method']:
            queryset = queryset.filter(
                sources__source_type__code=data['payment_method']).distinct()

        if data['status']:
            queryset = queryset.filter(status=data['status'])

        return queryset

    def update_grouporders(self, request):
        return render(request, "oscar/dashboard/grouporders/grouporders.html", {"grouporders": self.get_queryset().filter(id__gt=request.GET.get('last_id', 0))})

    def change_grouporder_statuses(self, request, grouporders):
        for grouporder in grouporders:
            self.change_grouporder_status(request, grouporder)
        return redirect('dashboard:grouporder-list')

    def change_grouporder_status(self, request, grouporder):
        if isinstance(grouporder, list):
            grouporder = grouporder[0]
        new_status = request.POST['new_status'].strip()
        if not new_status:
            messages.error(request, _("The new status '%s' is not valid")
                           % new_status)
        elif new_status not in grouporder.available_statuses():
            messages.error(request, _("The new status '%s' is not valid for"
                                      " this group order") % new_status)
        else:
            try:
                grouporder.set_status(new_status)
            except order_exceptions.InvalidOrderStatus:
                # The form should validate against this, so we should only end up
                # here during race conditions.
                messages.error(
                    request, _("Unable to change group order status as the requested "
                               "new status is not valid"))
        return render(request, "oscar/dashboard/grouporders/grouporders.html", {"grouporders": [grouporder]})

    def product_out_of_stock(self, request, grouporder):
        if isinstance(grouporder, list):
            grouporder = grouporder[0]

        lines = grouporder.get_all_lines().filter(
            product_id=request.POST.get('product', -1))

        for line in lines:
            line.out_of_stock()

        return render(request, "oscar/dashboard/grouporders/grouporders.html", {"grouporders": [GroupOrder.objects.get(pk=grouporder.pk)]})

    def download_selected_orders(self, request, grouporders):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' \
            % self.get_download_filename(request)
        writer = UnicodeCSVWriter(open_file=response)

        meta_data = (('number', _('Group Order number')),
                     ('value', _('Group Order value')),
                     ('date', _('Date of purchase')),
                     ('num_orders', _('Number of orders')),
                     ('status', _('Order status')),
                     ('supervisor', _('Supervisor email address')),
                     )
        columns = OrderedDict()
        for k, v in meta_data:
            columns[k] = v

        writer.writerow(columns.values())
        for grouporder in grouporders:
            row = columns.copy()
            row['number'] = grouporder.number
            row['value'] = grouporder.total_excl_tax
            row['date'] = format_datetime(
                grouporder.date_placed, 'DATETIME_FORMAT')
            row['num_orders'] = grouporder.num_orders
            row['status'] = grouporder.status
            row['supervisor'] = grouporder.user.email
            writer.writerow(row.values())
        return response

    def get_download_filename(self, request):
        return 'grouporders.csv'


class GroupOrderDetailView(views.OrderDetailView):
    """
    Dashboard view to display a single order.
    Supports the permission-based dashboard.
    """
    model = GroupOrder
    context_object_name = 'grouporder'
    template_name = 'oscar/dashboard/grouporders/grouporder_detail.html'

    # These strings are method names that are allowed to be called from a
    # submitted form.
    order_actions = ('change_order_status', 'change_grouporder_status')

    def get_object(self, queryset=None):
        return get_grouporder_for_user_or_404(
            self.request.user, self.kwargs['number'])

    def get_grouporder_orders(self):
        return self.object.orders.all()

    def post(self, request, *args, **kwargs):
        # For POST requests, we use a dynamic dispatch technique where a
        # parameter specifies what we're trying to do with the form submission.
        # We distinguish between order-level actions and line-level actions.

        grouporder = self.object = self.get_object()

        # Look for order-level action first
        if 'grouporder_action' in request.POST:
            return self.handle_order_action(
                request, grouporder, request.POST['grouporder_action'])

        if 'order_action' in request.POST:
            return self.handle_order_action(
                request, grouporder.orders.get(number=request.POST['order_number']), request.POST['order_action'])

        return self.reload_page(error=_("No valid action submitted"))

    def handle_order_action(self, request, order, action):
        if action not in self.order_actions:
            return self.reload_page(error=_("Invalid action"))
        return getattr(self, action)(request, order)

    def reload_page(self, fragment=None, error=None):
        url = reverse('dashboard:grouporder-detail',
                      kwargs={'number': self.object.number})
        if fragment:
            url += '#' + fragment
        if error:
            messages.error(self.request, error)
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        ctx = DetailView.get_context_data(self, **kwargs)

        # Forms
        #ctx['note_form'] = self.get_order_note_form()
        ctx['order_status_form'] = self.get_order_status_form()

        ctx['orders'] = self.get_grouporder_orders()
        ctx['order_statuses'] = Order.all_statuses()
        #ctx['payment_event_types'] = PaymentEventType.objects.all()

        #ctx['payment_transactions'] = self.get_payment_transactions()

        return ctx

    def change_order_status(self, request, order):
        form = self.get_order_status_form()
        if not form.is_valid():
            return self.reload_page(error=_("Invalid form submission"))

        old_status, new_status = order.status, form.cleaned_data['new_status']
        handler = EventHandler(request.user)

        success_msg = _(
            "Order status changed from '%(old_status)s' to "
            "'%(new_status)s'") % {'old_status': old_status,
                                   'new_status': new_status}
        try:
            handler.handle_order_status_change(
                order, new_status, note_msg=success_msg)
        # except PaymentError as e:
        #    messages.error(
        #        request, _("Unable to change order status due to "
        #                   "payment error: %s") % e)
        except order_exceptions.InvalidOrderStatus:
            # The form should validate against this, so we should only end up
            # here during race conditions.
            messages.error(
                request, _("Unable to change order status as the requested "
                           "new status is not valid"))
        else:
            messages.info(request, success_msg)
        return self.reload_page()

    # Data fetching methods for template context
    def change_grouporder_status(self, request, order):
        form = self.get_order_status_form()
        if not form.is_valid():
            return self.reload_page(error=_("Invalid form submission"))

        new_status = form.cleaned_data['new_status']

        try:
            order.set_status(new_status)
        except order_exceptions.InvalidOrderStatus:
            # The form should validate against this, so we should only end up
            # here during race conditions.
            messages.error(
                request, _("Unable to change order status as the requested "
                           "new status is not valid"))

        return self.reload_page()
