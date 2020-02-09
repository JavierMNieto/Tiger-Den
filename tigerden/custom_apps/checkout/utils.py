from oscar.apps.checkout import utils

class CheckoutSessionData(utils.CheckoutSessionData):
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
        