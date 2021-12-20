from django import template
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from sober.release import __version__
import markdown

register = template.Library()


# to access dict_items beginning with underscores
# useful for debugging
# source: https://stackoverflow.com/a/13694031/333403
@register.filter(name="get")
def get(d, k):
    return d.get(k, None)


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def render_markdown(txt):
    # !!! here we shoud check if there is no harmfull code in txt
    # because we will pass it through `safe` later
    # however it should be possible to discuss about code (even javascript)
    return markdown.markdown(txt)


@register.filter
def ensure_short_string(thestring, n_chars):
    assert n_chars > 3
    assert isinstance(n_chars, int)
    short_str = thestring
    if len(short_str) > n_chars:
        short_str = "{}...".format(short_str[: n_chars - 3])

    return short_str


@register.filter
def get_info_button_tags(button_type, brick):
    """
    This serves as a global dict-lookup for attributes of the info_button.
    It helps to avoid clumsy or abundant template files

    :param button_type:
    :param brick:
    :return:
    """

    if button_type == "pro":
        res = {
            "css1": "text-block-button-pro",
            "css3": "bgc_pro1",
            "head1": "pro: {}".format(brick.nbr_pro),
            "head_mo_title": "median vote",
            "head_value": 0,
            "head_line": _("Pro-Arguments"),
            "no_content_yet_msg": _("No Pro-Arguments yet."),
        }
    elif button_type == "contra":
        res = {
            "css1": "text-block-button-contra",
            "css3": "bgc_contra1",
            "head1": "contra: {}".format(brick.nbr_contra),
            "head_mo_title": _("median vote"),
            "head_value": 0,
            "head_line": _("Contra-Arguments"),
            "no_content_yet_msg": _("No Contra-Arguments yet."),
        }
        pass
    else:
        res = {
            "css1": "text-block-button-rest",
            "css3": "bgc_rest1",
            "head1": "rest: {}".format(len(brick.direct_children_rest)),
            "head_mo_title": _("median vote"),
            "head_value": 0,
            "head_line": _("Further Reactions"),
            "no_content_yet_msg": _("No Further Reactions yet."),
        }
        pass

    res["button_type"] = button_type

    return res


@register.filter
def get_child_type_list(button_type, brick):
    """
    Allows quick access to the relevant child list for different kinds of buttons

    :param button_type:
    :param brick:
    :return:
    """

    if button_type == "pro":
        return brick.direct_children_pro
    elif button_type == "contra":
        return brick.direct_children_contra
    else:
        return brick.direct_children_rest


@register.filter
def settings_value(name):
    """
    This filter serves to access the some values from settings.py inside the templates
    without passing them through the view.

    For security we only allow such values which are explictly mentioned here.
    (to e.g. prevent an adversary template author to access settings.DATABASES etc.)

    :param name:    name of the requested setting
    :return:
    """

    allowed_settings = ["DEBUG", "VERSION"]

    if name not in allowed_settings:
        msg = "using settings.{} is not explicitly allowed".format(name)
        raise ValueError(msg)

    if name == "VERSION":
        # tecnically this is not a setting, but it seems acceptable to distribute it this way
        return __version__
    else:
        return getattr(settings, name, False)


# maybe a restart of the server is neccessary after chanching this file
