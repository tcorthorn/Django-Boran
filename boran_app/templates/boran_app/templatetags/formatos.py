from django import template

register = template.Library()

@register.filter
def miles_punto(value):
    try:
        value = int(value)
        return '{0:,}'.format(value).replace(',', '.')
    except:
        return value
