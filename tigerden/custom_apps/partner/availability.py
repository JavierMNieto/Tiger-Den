from oscar.apps.partner import availability

class Base(availability.Base):
    extra_message = ''
    
class Unavailable(availability.Unavailable):
    def __init__(self, extra_message=''):
        super().__init__()
        self.extra_message = extra_message