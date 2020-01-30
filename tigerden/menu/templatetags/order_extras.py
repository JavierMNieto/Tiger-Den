from django import template
from datetime import datetime
from menu.forms import ItemForm

register = template.Library()

@register.filter(name='is_active_item')
def times(limited_time):
    # Return whether today is a valid time (represented from 0-6 for Monday-Sunday) for the limited item
    # TODO: Server is in utc time, so change time to local time to check currect day.
    #       Or, check the time on the frontend
    return limited_time < 0 or limited_time == datetime.today().weekday()

@register.filter(name='get_item_form')
def get_item_form(item_id):
    # Generate item form of specified item id
    return ItemForm(initial={'id': item_id})
