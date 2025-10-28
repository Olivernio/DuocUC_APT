from django import template
from cart.utils import get_or_create_cart #

register = template.Library()

@register.simple_tag(takes_context=True)
def get_cart(context):
    request = context['request']
    return get_or_create_cart(request)

@register.filter
def cart_item_count(cart):
    if cart:
        return cart.total_items #
    return 0