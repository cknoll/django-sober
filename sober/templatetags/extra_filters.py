from django import template

register = template.Library()


# to access dict_items beginning with underscores
# useful for debugging
# source: https://stackoverflow.com/a/13694031/333403
@register.filter(name='get')
def get(d, k):
    return d.get(k, None)


@register.filter
def subtract(value, arg):
    return value - arg

# maybe a restart of the server is neccessary after chanching this file
