from oscar.apps.checkout import mixins
from oscar.core.loading import get_model
from decimal import Decimal as D
from django.http import HttpResponseRedirect
GroupOrder = get_model('order', 'GroupOrder')

logger = mixins.logger

class OrderPlacementMixin(mixins.OrderPlacementMixin):
    def handle_payment(self, order_number, total, **kwargs):
        """
        Override handle payment call
        """
        pass
    
    def handle_order_placement(self, order_number, user, basket,
                               shipping_address, shipping_method,
                               shipping_charge, billing_address, order_total, 
                               location, **kwargs):
        """
        Write out the order models and return the appropriate HTTP response
        We deliberately pass the basket in here as the one tied to the request
        isn't necessarily the correct one to use in placing the order.  This
        can happen when a basket gets frozen.
        """
        order = self.place_order(
            order_number=order_number, user=user, basket=basket,
            shipping_address=shipping_address, shipping_method=shipping_method,
            shipping_charge=shipping_charge, order_total=order_total,
            billing_address=billing_address, **kwargs)
        basket.submit()
        
        if user.is_authenticated and user.is_supervisor():
            self.handle_requests_placement(user, order_number, location, order.currency)
        
        return self.handle_successful_order(order)
    
    def handle_requests_placement(self, user, order_number, location, currency):
        reqs_total = D('0.00')
        reqs = user.get_order_requests()
        
        if reqs:
            for req in reqs.all():
                reqs_total += req.total_excl_tax
        
        group_order = GroupOrder(number=order_number, 
                                user=user, 
                                total_excl_tax=reqs_total,
                                status=GroupOrder.all_statuses()[0],
                                location=location,
                                currency=currency)
        group_order.save()
        
        if reqs:
            for req in reqs.all():
                req.group_order_id = group_order.id
                req.save()
                
                # Send confirmation message (normally an email)
                self.send_confirmation_message(req, self.communication_type_code)
                
        group_order.set_status(GroupOrder.all_statuses()[1])
        
        self.checkout_session.flush()

        # Save order id in session so thank-you page can load it
        
        self.request.session['checkout_order_id'] = group_order.orders.first().id
        return HttpResponseRedirect(self.get_success_url())
    
    def handle_successful_order(self, order):
        """
        Handle the various steps required after an order has been successfully
        placed.

        Override this view if you want to perform custom actions when an
        order is submitted.
        """
        # Send confirmation message (normally an email)
        #self.send_confirmation_message(order, self.communication_type_code)

        # Flush all session data
        self.checkout_session.flush()

        # Save order id in session so thank-you page can load it
        self.request.session['checkout_order_id'] = order.id

        response = HttpResponseRedirect(self.get_success_url())
        self.send_signal(self.request, response, order)
        return response