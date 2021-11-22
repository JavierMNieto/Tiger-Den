from oscar.apps.order.processing import EventHandler as CustomEventHandler


class EventHandler(CustomEventHandler):
    def handle_order_status_change(self, order, new_status, note_msg=None, code=None):
        """
        Handle a requested order status change

        This method is not normally called directly by client code.  The main
        use-case is when an order is cancelled, which in some ways could be
        viewed as a shipping event affecting all lines.
        """
        order.set_status(new_status, code)
        if note_msg:
            self.create_note(order, note_msg)
