import collections
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import LANGUAGE_SESSION_KEY, gettext_lazy as _
from django.utils import translation
from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.decorators import login_required

from .models import Brick, SettingsBunch, User
from .simple_pages import defdict as sp_defdict
from .forms import forms
from .language import lang

from . import model_helpers as mh

from ipydex import IPS


global_lc = mh.global_lc


# empty object to store some attributes at runtime
class Container(object):
    pass


auth_views.LoginView.template_name = "sober/main_login.html"


def view_logout(request):
    c = Container()

    if not request.user.is_authenticated:
        c.utc_comment = "utc_logout_page_not_logged_in"
        content1 = _("You are cannot log out because you are currently not logged in.")
    else:
        logout(request)
        c.utc_comment = "utc_logout_page_logout_success"
        content1 = _("Successfully logged out.")

    content2 = _("Go back to main page.")
    # todo: A href here would be nice but I dont want the safe filter for the whole content
    c.content = "{}\n{}".format(content1, content2)

    return render(request, 'sober/main_simple_page.html', {"sp": c})


def view_register(request):
    """
    Render dummy static page
    :param request:
    :return:
    """
    set_language_from_settings(request)

    c = Container()
    c.content = _("In the future there will be a page for registration here. "
                  "Meanwhile contact the admin for a new account")
    c.utc_comment = "utc_registration_page"

    context = {"sp": c}
    return render(request, 'sober/main_simple_page.html', context)


@login_required
def view_profile(request):
    """
    Render dummy static page
    :param request:
    :return:
    """
    set_language_from_settings(request)

    c = Container()
    c.content = _("In the future there will be a profile page here.")
    c.utc_comment = "utc_profile_page"

    context = {"sp": c}
    return render(request, 'sober/main_simple_page.html', context)


def view_debug(request, **kwargs):
    """
    This view serves to easily print debug information during development process

    :param request:
    :return:
    """
    import os
    import inspect
    c = Container()
    c.utc_comment = "utc_debug_page"
    c.data = collections.OrderedDict()
    c.data["sober_path"] = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    c.data["kwargs"] = kwargs

    c.data["the_user"] = request.user
    c.data["the_user_a"] = request.user.is_authenticated
    c.data["the_user_n"] = request.user.get_username()

    return render(request, 'sober/main_debug.html', {"c": c})


# this will be obsolete once we have a profile link or menu
@login_required
def view_debug_login(request, **kwargs):
    """this serves to test the login functionality"""
    return view_debug(request, **kwargs)


def view_index(request):
    # Currently the landing page is a list of theses
    # in the future this will change
    return view_thesis_list(request)


def view_thesis_list(request):
    """
    Show a chronological ordered list of theses

    :param request:
    :return:
    """
    set_language_from_settings(request)

    # get a list of all thesis-bricks

    thesis_list = Brick.objects.filter(type=Brick.thesis)
    thesis_list = thesis_list.order_by("-update_datetime")

    base_object = Container()
    base_object.page_options = Container()
    base_object.page_options.page_type = "list_of_theses"
    base_object.page_options.special_head_link = "new_thesis_link"
    # !! hcl
    base_object.page_options.title = _("List of Theses")

    for tbrick in thesis_list:
        # trigger processing of the root of the respective trees (sufficient for the index)
        mh.BrickTree(tbrick, max_alevel=0)

    base_object.sorted_child_list = thesis_list

    # list of theses -> we can savely hardcode the bb_alevel to 0
    base_object.page_options.bb_alevel = 0
    return render(request, 'sober/main_brick_tree.html', {'base': base_object})


def view_simple_page(request, pagetype=None):
    """
    Render (almost) static page
    :param request:
    :param pagetype:
    :return:
    """
    set_language_from_settings(request)

    context = {"pagetype": pagetype, "sp": sp_defdict[pagetype]}
    return render(request, 'sober/main_simple_page.html', context)


def view_renderbrick(request, brick_id=None):
    """
    Top level rendering of a brick

    :param request:
    :param brick_id:
    :return:
    """
    set_language_from_settings(request)

    base_brick = get_object_or_404(Brick, pk=brick_id)

    base_brick.page_options = Container()
    base_brick.page_options.page_type = "brick_detail"

    bt = mh.BrickTree(base_brick)  # process the complete tree
    base_brick.sorted_child_list = bt.get_processed_subtree_as_list(base_brick)
    base_brick.page_options.bb_alevel = base_brick.absolute_level
    return render(request, 'sober/main_brick_tree.html', {'base': base_brick})


def view_new_brick(request, brick_id=None, type_code=None):
    """
    create a new brick of a given type (render form)

    :param request:
    :param brick_id:
    :param type_code: one of {th, pa, ca, qu, is}
    :return:
    """
    set_language_from_settings(request)

    if type_code not in Brick.typecode_map.keys():
        raise ValueError("Invalid type_code `{}` for Brick".format(type_code))

    # sp = simple page
    sp = Container()
    sp.page_options = Container()
    sp.page_options.title = "New {1}-Brick to {0}".format(brick_id, type_code)

    sp.long_brick_type = lang[global_lc]['long_brick_type'][type_code]

    if type_code == Brick.reverse_typecode_map[Brick.thesis]:
        # ensure that we come from the correct url-dispatcher
        assert brick_id == -1
        sp.parent_brick = None
        bt = None
        sp.page_options.bb_alevel = 0

    else:
        parent_brick = get_object_or_404(Brick, pk=brick_id)
        bt = mh.BrickTree(entry_brick=parent_brick, max_rlevel=1)

        # use the processed version of base_brick
        sp.parent_brick = bt.get_processed_subtree_as_list(base_brick=parent_brick, max_rlevel=0)[0]
        sp.page_options.bb_alevel = sp.parent_brick.absolute_level

    # here we process the submitted form
    if request.method == 'POST':
        brickform = forms.BrickForm(request.POST)

        if not brickform.is_valid():
            # render some error message here
            sp.content = "Errors: {}<br>{}".format(brickform.errors, brickform.non_form_errors)

        else:
            new_brick = brickform.save(commit=False)
            new_brick.parent = sp.parent_brick
            new_brick.type = Brick.typecode_map[type_code]
            new_brick.save()

            if sp.parent_brick:
                # new generation of the tree because the number of childs has changed

                bt = mh.BrickTree(entry_brick=sp.parent_brick, max_rlevel=1)
                parent, child = bt.get_processed_subtree_as_list(sp.parent_brick,
                                                                 max_rlevel=1,
                                                                 child_filter=[new_brick.pk])
                # bb_alevel has not changed, no need to reassign
            else:
                parent = None
                bt = mh.BrickTree(entry_brick=new_brick, max_rlevel=1)
                child = bt.get_processed_subtree_as_list(base_brick=new_brick, max_rlevel=0)[0]
                sp.page_options.bb_alevel = child.absolute_level

            sp.parent_brick, sp.newly_fabricated_brick = parent, child
            sp.utc_comment = "utc_form_successfully_processed"
            sp.content = "no errors. Form saved. Result: {}".format(new_brick)

    # here we handle the generation of an empty form
    else:
        brickform = forms.BrickForm()
        sp.content = ""
        sp.form = brickform

    if hasattr(sp, "form"):

        if type_code == Brick.reverse_typecode_map[Brick.thesis]:
            sp.form.action_url_name = "new_thesis"
        else:
            sp.form.action_url_name = "new_brick"

    context = {"pagetype": "New-Brick-Form", "sp": sp, "brick_id": brick_id, "type_code": type_code}
    return render(request, 'sober/main_simple_page.html', context)


def view_edit_brick(request, brick_id=None):
    set_language_from_settings(request)

    sp = Container()
    sp.page_options = Container()

    sp.brick_to_edit = get_object_or_404(Brick, pk=brick_id)

    type_code = Brick.reverse_typecode_map[sp.brick_to_edit.type]
    sp.long_brick_type = lang[global_lc]['long_brick_type'][type_code]
    sp.page_options.title = "Edit {1}-Brick with {0}".format(brick_id, sp.long_brick_type)

    # here we process the submitted form
    if request.method == 'POST':
        brickform = forms.BrickForm(request.POST, instance=sp.brick_to_edit)

        if not brickform.is_valid():
            # render some error message here
            sp.content = "Errors: {}<br>{}".format(brickform.errors, brickform.non_form_errors)

        else:
            edited_brick = brickform.save(commit=False)
            edited_brick.update_datetime = timezone.now()
            edited_brick.save()

            bt = mh.BrickTree(entry_brick=edited_brick, max_rlevel=0)

            sp.newly_fabricated_brick = bt.get_processed_subtree_as_list(base_brick=edited_brick,
                                                                         max_rlevel=0)[0]

            sp.utc_comment = "utc_form_successfully_processed"
            sp.page_options.bb_alevel = sp.newly_fabricated_brick.absolute_level
            sp.preview_flag = True
            sp.content = "{} {}.".format(_("Successfully updated brick with ID "), str(edited_brick.pk))

    # here we handle the generation of an empty form
    else:
        brickform = forms.BrickForm(instance=sp.brick_to_edit)
        sp.content = ""
        sp.form = brickform

    if hasattr(sp, "form"):
        sp.form.action_url_name = "edit_brick"

    context = {"pagetype": "Brick-Edit-Form", "sp": sp, "brick_id": brick_id, "type_code": None}
    return render(request, 'sober/main_simple_page.html', context)


def view_settings_dialog(request):
    """
    Change the settings. (Language, default-discussion-depth)

    :param request:
    :return:

    There are 3 sources of settings:
        - first contact, not logged in: default settings (pk=1)
        - not first contact, not logged in: session
        - logged in: user.settings

    There are 2 targets for (changed) settings:
        - session (always)
        - user.settings (only for logged in users)
    """
    sn = request.session

    sp = Container()
    sp.mysession = sn

    if request.method != 'POST':
        # here we initially show the form (not the posted form)
        sp.content = "request.session: {}".format(dict(sn))  # debug

        leagacy_settings = get_settings_object(request)
        sp.form = forms.SettingsForm(instance=leagacy_settings)

    else:
        # here we process the submitted form

        settings_instance = get_settings_object(request)
        settingsform = forms.SettingsForm(request.POST, instance=settings_instance)

        if request.user.is_authenticated:
            settings_bunch_object = settingsform.save()
        else:
            # Attention: we do not save the settings_bunch_object to the database here. We just create it.
            settings_bunch_object = settingsform.save(commit=False)

        # TODO: remove settings_bunch_object

        # In any case we save a settings_dict in the session
        sdict = settings_bunch_object.get_dict()
        sn["settings_dict"] = sdict

        set_language_from_settings(request)
        sp.content = "request.session: {}".format(dict(sn))
        sp.content += "\nSettings saved."

        # due to a unexpected behavior language is not changed in the first response
        # see https://stackoverflow.com/questions/52233911/django-languange-change-takes-effect-only-after-reload

    if hasattr(sp, "form"):
        sp.form.action_url_name = "settings_dialog"

    context = {"pagetype": "Settings-Form", "sp": sp}
    return render(request, 'sober/main_settings_page.html', context)

# ------------------------------------------------------------------------
# below are auxiliary functions and classes which do not directly produce a view
# ------------------------------------------------------------------------


def get_settings_object(request):
    """
    Returns either the settings from user.settings or form the session or simply
    a new object with default values.

    :param request:
    :return:
    """

    if request.user.is_authenticated:
        user = get_object_or_404(User, pk=request.user.pk)
        settings_instance = user.soberuser.settings
    else:
        # try to load settings from the session
        settings_dict = request.session.get("settings_dict")

        if settings_dict is None:
            # pk=1 loads (by convention) the default settings for non-logged-in users
            default_settings = get_object_or_404(SettingsBunch, pk=1)
            settings_instance = SettingsBunch(**default_settings.get_dict())
        else:
            settings_instance = SettingsBunch(**settings_dict)

    return settings_instance


def set_language_from_settings(request):
    """
    Set the session variable which is evaluated by django to define the language.
    see https://stackoverflow.com/questions/2605384/how-to-explicitly-set-django-language-in-django-session
    :param request:
    :return:
    """
    # has this be really to be called in every view?
    # !! after implementing user-login this probably has to be adapted

    sn = request.session
    sdict = sn.get("settings_dict")
    if sdict is not None:
        lang_from_settings = sdict['language']
        translation.activate(lang_from_settings)
        sn[LANGUAGE_SESSION_KEY] = lang_from_settings
