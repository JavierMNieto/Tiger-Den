from oscar.apps.checkout import mixins
from oscar.core.loading import get_model

GroupOrder = get_model('grouporder', 'GroupOrder')

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
        
        if user.is_supervisor():
            group_order = GroupOrder(number=order_number, 
                                    user=user, 
                                    total_excl_tax=order_total.excl_tax,
                                    status=GroupOrder.all_statuses()[0],
                                    location=location)
            group_order.save()
            reqs = user.get_order_requests()
            if reqs:
                for req in reqs.all():
                    req.group_order_id = group_order.id
                    req.save()
                    
                    # Send confirmation message (normally an email)
                    self.send_confirmation_message(req, self.communication_type_code)
            
            group_order.set_status(GroupOrder.all_statuses()[1])
        
        return self.handle_successful_order(order)
    
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