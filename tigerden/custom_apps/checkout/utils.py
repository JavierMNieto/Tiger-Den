from oscar.apps.checkout import utils


class CheckoutSessionData(utils.CheckoutSessionData):
    def set_guest_name(self, name):
        self._set('guest', 'name', name)

    def get_guest_name(self):
        return self._get('guest', 'name')

    def set_supervisor(self, supervisor_pk):
        self._check_namespace('submission')
        self._set('submission', 'supervisor', supervisor_pk)

    def supervisor(self):
        return self._get('submission', 'supervisor')

    def is_supervisor_set(self):
        return self._get('submission', 'supervisor', False)

    def set_location(self, location):
        self._check_namespace('submission')
        self._set('submission', 'location', location)

    def location(self):
        return self._get('submission', 'location')

    def is_location_set(self):
        return self._get('submission', 'location', False)

    def is_payment_method_set(self):
        return self._get('payment', 'method', False)

    def set_max_credit(self, max_credit):
        self._check_namespace('submission')
        self._set('submission', 'max_credit_allocation', max_credit)

    def max_credit(self):
        return self._get('submission', 'max_credit_allocation')

    def is_max_credit(self):
        return self._get('submission', 'max_credit_allocation', False)
