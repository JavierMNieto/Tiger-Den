from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
import json

from . import models, forms

def index(request):
    return render(request, "menu/index.html", {"items": models.Item.objects.all()})

def order(request):
    return render(request, "menu/order_submitted.html", {"items": request.POST.getlist("items[]")})

def add_item(request):
    """Add Item to cart through customer's cached session

        cart = {
            'ITEM_ID': QUANTITY,
            ...
        }

        TODO: Save item options for items such as Coffee
    """
    if request.method == 'POST':
        form = forms.ItemForm(request.POST)

        cart = json.loads(request.session.get('cart', r'{}'))
        
        if form.is_valid():
            item_id = str(form.cleaned_data["id"])
            if item_id in cart:
                cart[item_id] += int(form.cleaned_data["quantity"])
            else:
                cart[item_id] = int(form.cleaned_data["quantity"])
            
            if cart[item_id] < 1:
                del cart[item_id]

        cart = json.dumps(cart)
        request.session['cart'] = cart

        return JsonResponse(cart, safe=False)
    
    return Http404()
