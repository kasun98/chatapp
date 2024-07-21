from django import template

register = template.Library()

@register.filter
def truncate_chars(value, length):
    """
    Truncate a string after a certain number of characters.
    """
    if len(value) > length:
        return value[:length] + '...'
    return value