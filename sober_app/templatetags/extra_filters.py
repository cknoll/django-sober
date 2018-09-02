from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    return value - arg

# maybe a restart of the server is neccessary after chanching this file
