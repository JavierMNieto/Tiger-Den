from django.contrib.auth.models import User
from django.db import models
from django.utils.html import mark_safe
from django.core.validators import MinValueValidator
from datetime import datetime, timezone

class Item(models.Model):
    """Tiger Den product model
        
    """

    #image = models.ImageField(upload_to="static/images")

    name        = models.CharField(max_length=50)
    description = models.TextField(max_length=250)
    price       = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])

    # Numbers (besides 'Every Day' option) that represent days from python datatime class
    # representing what day of the week the item is available
    LIMITED_TIME_CHOICES = [
        (-1, 'Every Day'),
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    limited_time = models.IntegerField(choices=LIMITED_TIME_CHOICES, default=-1)

    # Categories with sub categories
    CATEGORY_CHOICES = [
        ('Drinks', (
                ('', 'Other'),
                ('hot', 'Hot'),
                ('cold', 'Cold'),
            )
        ),
        ('food', 'Food')
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='food')

    def __str__(self):
        return self.name
    
    """
    def image_tag(self):
        return mark_safe('<img src="/%s" width="128" height="128"/>' % (self.image.url))

        image.short_description = 'Image'
        image.allow_tags = True
    """

class BasicOrder():
    """Class representing what every order Model should have included
        total, formatted_total
    """
    def total(self):
        # Return total price of order
        pass

    def formatted_total(self):
        # Return total in USD money format
        return "${:0.2f}".format(self.total())

class GroupOrder(models.Model, BasicOrder):
    """Order actually submitted to Tiger Den for delivery

        Contains relationship to complete orders from individuals
        Relates to user who submitted the group order

        Order -> GroupOrder -> User
    """
    user     = models.ForeignKey(User, related_name='group_orders', on_delete=models.CASCADE)
    location = models.CharField(max_length=50)

    # More BooleanFields for stages of production?
    confirmed  = models.BooleanField()

    created_at  = models.DateTimeField(auto_now_add=True)

    def total(self):
        total = 0.0
        for o in self.orders.all():
            total += o.total()
        
        return total

    def order_time(self):
        # Format utc into local time
        # TODO: Investigate server's time being inaccurate?
        return self.created_at.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%B %d, %Y %I:%M:%S %p")

class Order(models.Model, BasicOrder):
    """Complete order of an individual customer

        Contains relationship to each item order in customer's 'cart'
        Relates to Final Group Order for submission

        ItemOrder -> Order -> GroupOrder
    """
    name        = models.CharField(max_length=50)
    group       = models.ForeignKey("GroupOrder", related_name="orders", on_delete=models.CASCADE)
    accepted    = models.BooleanField()

    def __str__(self):
        return str(self.id)

    def total(self):
        total = 0.0
        for i in self.item_orders.all():
            total += i.total()
        
        return total

class ItemOrder(models.Model, BasicOrder):
    """Individual Item Order in customer's 'cart'

        TODO: Add verification for limited time item for if it's actually available
    """
    item       = models.ForeignKey("Item", related_name="item_orders", on_delete=models.CASCADE)
    order      = models.ForeignKey("Order", related_name="item_orders", on_delete=models.CASCADE)
    quantity   = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    item_price = models.IntegerField(default=0, validators=[MinValueValidator(0)]) # price of item at time of order

    class Meta:
        unique_together = ('order', 'item')

    def total(self):
        return self.quantity*self.item_price

    def __str__(self):
        return str(self.id)

class ItemOption(models.Model):
    """Specification of an Item
        Ex: Type of cream in Coffee
    """
    pass