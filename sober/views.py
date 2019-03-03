import collections
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, get_language
from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.core.exceptions import PermissionDenied

from .models import Brick, User, AuthGroup
from .simple_pages import defdict as sp_defdict
from .forms import forms
from .language import lang

import urllib  # (only for the qnd hack ViewMdPreview)

from .model_helpers import Container
from . import model_helpers as mh

# noinspection PyUnresolvedReferences
from ipydex import IPS


# global language code
global_lc = mh.global_lc

# TODO: this should live in an auxilliary module


class DataIntegrityError(ValueError):
    pass


# noinspection PyClassHasNoInit
class ViewAdaptedLogin(auth_views.LoginView):
    template_name = 'sober/main_login.html'

    # noinspection PyMethodOverriding
    def post(self, request):
        response = super().post(request)

        settings = mh.get_settings_object(request)
        request.session["settings_dict"] = settings.get_dict()
        mh.set_language_from_settings(request)

        return response


def view_logout(request):
    mh.set_language_from_settings(request)

    sd = request.session.get("settings_dict")
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

    request.session["settings_dict"] = sd

    base = Container()
    endow_base_object(base, request)

    context = {"sp": c, "base": base}

    return render(request, 'sober/main_simple_page.html', context)


def view_register(request):
    """
    Render dummy static page
    :param request:
    :return:
    """
    mh.set_language_from_settings(request)

    c = Container()
    c.content = _("In the future there will be a page for registration here. "
                  "Meanwhile contact the admin for a new account")
    c.utc_comment = "utc_registration_page"

    base = Container()
    endow_base_object(base, request)

    context = {"sp": c, "base": base}
    return render(request, 'sober/main_simple_page.html', context)


@login_required
def view_profile(request):
    """
    Render dummy static page
    :param request:
    :return:
    """
    mh.set_language_from_settings(request)

    data = Container()
    data.utc_comment = "utc_profile_page"
    data.username = request.user
    data.activity_list = "In the future there will be a list of recent edits, votes etc here."

    base = Container()
    endow_base_object(base, request)

    context = {"data": data, "base": base}
    return render(request, 'sober/main_profile_page.html', context)


def view_debug(request, **kwargs):
    """
    This view serves to easily print debug information during development process

    :param request:
    :return:
    """
    import os
    import inspect
    from . import utils

    utils.ensure_data_integrity()

    c = Container()
    c.utc_comment = "utc_debug_page"
    c.data = collections.OrderedDict()
    c.data["sober_path"] = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    c.data["kwargs"] = kwargs

    c.data["the_user"] = request.user
    c.data["the_user_a"] = request.user.is_authenticated
    c.data["the_user_n"] = request.user.get_username()
    c.data["sdict"] = request.session.get("settings_dict")
    c.data["language"] = get_language()

    base = Container()
    endow_base_object(base, request)

    context = {"c": c, "base": base}
    return render(request, 'sober/main_debug.html', context)


# this will be obsolete once we have a profile link or menu
@login_required
def view_debug_login(request, **kwargs):
    """this serves to test the login functionality"""
    return view_debug(request, **kwargs)


def view_index(request):
    """
    Render the landing page:
    :param request:
    :return:
    """
    mh.set_language_from_settings(request)

    base_object = mh.prepare_thesis_list(request)

    base_object.top_content = sp_defdict["landing_page"].content

    endow_base_object(base_object, request)

    context = {"base": base_object}

    return render(request, 'sober/main_brick_tree.html', context)


def view_thesis_list(request):

    base_object = mh.prepare_thesis_list(request)
    endow_base_object(base_object, request)
    context = {"base": base_object}

    return render(request, 'sober/main_brick_tree.html', context)


def view_simple_page(request, pagetype=None):
    """
    Render (almost) static page
    :param request:
    :param pagetype:
    :return:
    """
    mh.set_language_from_settings(request)

    # TODO: merge the base-object and the sp-object
    base = Container()
    endow_base_object(base, request)

    context = {"pagetype": pagetype, "sp": sp_defdict[pagetype], "base": base}
    return render(request, 'sober/main_simple_page.html', context)


class ViewRenderBrick(View):
    """
    Normal view has get and post. Post serves to handle the vote-form.
    """

    # noinspection PyMethodMayBeStatic
    def get(self, request, tree_base_brick_id=None):
        """
        Top level rendering of a brick

        :param request:
        :param tree_base_brick_id:
        :return:
        """
        mh.set_language_from_settings(request)
        base_brick = self.create_brick_page(tree_base_brick_id)
        endow_base_object(base_brick, request)

        return render(request, 'sober/main_brick_tree.html', {'base': base_brick})

    @staticmethod
    def create_brick_page(tree_base_brick_id=None):
        """
        This method does the main work for the get-method, but does not depend on the request.
        Thus it can easily be called from other views.

        :param tree_base_brick_id:
        :return: <base-brick-object>
        """
        base_brick = get_object_or_404(Brick, pk=tree_base_brick_id)

        base_brick.page_options = Container()
        base_brick.page_options.page_type = "brick_detail"

        bt = mh.BrickTree(base_brick)  # process the complete tree
        base_brick.sorted_child_list = bt.get_processed_subtree_as_list(base_brick)
        base_brick.page_options.bb_alevel = base_brick.absolute_level
        base_brick.brick_tree = bt
        return base_brick


    def post(self, request, tree_base_brick_id):
        """
        handle the vote-form

        :param request:
        :param tree_base_brick_id:
        :return:
        """
        if not request.user.is_authenticated:
            return view_simple_page(request, pagetype="voting_not_allowed_login")

        # Note: tree_base_brick_id is the "tree_root" of the sending brick_tree_view (i.e., uppermost brick)
        # the brick for which the user has voted is written in the following hidden field

        current_brick = get_object_or_404(Brick, pk=int(request.POST["vote_brick"]))
        all_votes = current_brick.vote_set.all()

        current_user_votes = all_votes.filter(user=request.user)
        if len(current_user_votes) == 0:
            vote_form = forms.VoteForm(request.POST)
            vote_object = vote_form.save(commit=False)
            vote_object.user = request.user
            vote_object.brick = current_brick
        elif len(current_user_votes) == 1:
            # the user voted before on this brick
            vote_object = current_user_votes[0]
            vote_form = forms.VoteForm(data=request.POST, instance=vote_object)
            vote_form.save(commit=False)
        else:
            msg = "There are multiple votes for user {} and brick {}".format(request.user.pk, tree_base_brick_id)
            raise DataIntegrityError(msg)

        vote_object.save()

        # now recalculate the average vote of the brick
        all_votes = current_brick.vote_set.all()
        avg = sum([v.value for v in all_votes]) / len(all_votes)
        current_brick.cached_avg_vote = avg
        current_brick.save()

        return self.get(request, tree_base_brick_id)


class ViewNewBrick(View):
    """
    create a new brick of a given type (render form and process this form)
    """

    def __init__(self):
        super().__init__()
        self.sp = Container()
        self.thesis_flag = None
        self.allowed_groups = None

    def common(self, request, brick_id, type_code):
        """
        perform the steps which are in common for get and post
        :param request:
        :param brick_id:    id of the parent brick (-1 for thesis)
        :param type_code: one of {th, pa, ca, qu, is}
        :return:
        """
        mh.set_language_from_settings(request)

        if type_code not in Brick.typecode_map.keys():
            raise ValueError("Invalid type_code `{}` for Brick".format(type_code))

        # True if we create a thesis here
        self.thesis_flag = type_code == Brick.reverse_typecode_map[Brick.thesis]
        self.allowed_groups = mh.get_allowed_groups(request)

        # sp = simple page
        self.sp.page_options = Container()
        self.sp.page_options.title = "New {1}-Brick to {0}".format(brick_id, type_code)

        self.sp.long_brick_type = lang[global_lc]['long_brick_type'][type_code]

        if type_code == Brick.reverse_typecode_map[Brick.thesis]:
            # ensure that we come from the correct url-dispatcher
            assert brick_id == -1  # no parent brick for a new thesis
            self.sp.parent_brick = None
            self.sp.page_options.bb_alevel = 0

        else:
            parent_brick = get_object_or_404(Brick, pk=brick_id)
            bt = mh.BrickTree(entry_brick=parent_brick, max_rlevel=1)

            # use the processed version of base_brick
            self.sp.parent_brick = bt.get_processed_subtree_as_list(base_brick=parent_brick, max_rlevel=0)[0]
            self.sp.page_options.bb_alevel = self.sp.parent_brick.absolute_level

    def get(self, request, brick_id=None, type_code=None):
        """
        Handle generation of the empty form

        :param request:
        :param brick_id:
        :param type_code:
        :return:
        """
        mh.ensure_login(request)

        self.common(request, brick_id, type_code)

        if self.thesis_flag:
            brickform = forms.BrickForm(keep_group_fields=True, allowed_groups=self.allowed_groups)
        else:
            brickform = forms.BrickForm(allowed_groups=self.allowed_groups)
        self.sp.content = ""
        self.sp.form = brickform

        if self.thesis_flag:
            self.sp.form.action_url_name = "new_thesis"
        else:
            self.sp.form.action_url_name = "new_brick"

        base = Container()
        endow_base_object(base, request)

        context = {"pagetype": "New-Brick-Form", "sp": self.sp,
                   "brick_id": brick_id, "type_code": type_code,
                   "base": base}
        return render(request, 'sober/main_simple_page.html', context)

    def post(self, request, brick_id=None, type_code=None):
        """
        Handle processing of the form

        :param request:
        :param brick_id:
        :param type_code:
        :return:
        """

        mh.ensure_login(request)

        self.common(request, brick_id, type_code)
        if self.thesis_flag:
            brickform = forms.BrickForm(request.POST, keep_group_fields=True, allowed_groups=self.allowed_groups)
        else:
            brickform = forms.BrickForm(request.POST, allowed_groups=self.allowed_groups)

        if not brickform.is_valid():
            # error handling
            self.sp.content = mh.handle_form_errors(brickform)
            new_brick = None

            context = {"pagetype": "New-Brick-Form", "sp": self.sp, "brick_id": brick_id, "type_code": type_code}
            return render(request, 'sober/main_simple_page.html', context)

        else:
            new_brick = brickform.save(commit=False)
            new_brick.parent = self.sp.parent_brick
            new_brick.type = Brick.typecode_map[type_code]
            new_brick.save()

            root_parent = new_brick.get_root_parent()[0]

            rp_groups = {root_parent.associated_group}.union(
                                set(root_parent.allowed_for_additional_groups.all()))

            if not rp_groups.intersection(self.allowed_groups):
                # !! hcl
                errmsg = "The current user is not allowed to create/edit in these groups."

                # reason for not blocking .save() above: finding the root parent would not work
                new_brick.delete()
                raise PermissionDenied(errmsg)

            if self.thesis_flag:
                assert root_parent == new_brick
                base_brick_id = new_brick.pk
            else:
                base_brick_id = new_brick.parent.pk
                new_brick.associated_group = root_parent.associated_group
                new_brick.allowed_for_additional_groups.set( root_parent.allowed_for_additional_groups.all() )

            if self.sp.parent_brick:
                # new generation of the tree because the number of childs has changed

                bt = mh.BrickTree(entry_brick=self.sp.parent_brick, max_rlevel=1)
                parent, child = bt.get_processed_subtree_as_list(self.sp.parent_brick,
                                                                 max_rlevel=1,
                                                                 included_childs=[new_brick.pk])
                # bb_alevel has not changed, no need to reassign
            else:
                parent = None
                bt = mh.BrickTree(entry_brick=new_brick, max_rlevel=1)
                child = bt.get_processed_subtree_as_list(base_brick=new_brick, max_rlevel=0)[0]
                # noinspection PyUnresolvedReferences
                self.sp.page_options.bb_alevel = child.absolute_level

            self.sp.parent_brick, self.sp.newly_fabricated_brick = parent, child
            self.sp.utc_comment = "utc_form_successfully_processed"
            self.sp.content = "no errors. Form saved. Result: {}".format(new_brick)

        url = reverse("show_brick", kwargs={"tree_base_brick_id": root_parent.pk})
        final_url = "{}#{}".format(url, new_brick.pk)
        return redirect(final_url)


def view_edit_brick(request, brick_id=None):
    mh.set_language_from_settings(request)

    mh.ensure_login(request)

    sp = Container()
    sp.page_options = Container()

    sp.brick_to_edit = get_object_or_404(Brick, pk=brick_id)

    type_code = Brick.reverse_typecode_map[sp.brick_to_edit.type]
    sp.long_brick_type = lang[global_lc]['long_brick_type'][type_code]
    sp.page_options.title = "Edit {1}-Brick with {0}".format(brick_id, sp.long_brick_type)

    # TODO  avoid that a brick from a not allowed group is access (neither r nor w)
    allowed_groups = mh.get_allowed_groups(request)

    # here we process the submitted form
    if request.method == 'POST':
        brickform = forms.BrickForm(request.POST, instance=sp.brick_to_edit, allowed_groups=allowed_groups)

        if not brickform.is_valid():

            sp.content = mh.handle_form_errors(brickform)

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
        brickform = forms.BrickForm(instance=sp.brick_to_edit, allowed_groups=allowed_groups)
        sp.content = ""
        sp.form = brickform

    if hasattr(sp, "form"):
        sp.form.action_url_name = "edit_brick"

    base = Container()
    endow_base_object(base, request)

    context = {"pagetype": "Brick-Edit-Form", "sp": sp,
               "brick_id": brick_id, "type_code": None,
               "base": base}
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

        leagacy_settings = mh.get_settings_object(request)
        sp.form = forms.SettingsForm(instance=leagacy_settings)

    else:
        # here we process the submitted form

        settings_instance = mh.get_settings_object(request)
        settingsform = forms.SettingsForm(request.POST, instance=settings_instance)

        if request.user.is_authenticated:
            settingsform.save()
        else:
            # Attention: we do not save the settings_bunch_object to the database here. We just create it.
            settingsform.save(commit=False)

        # In any case we save a settings_dict in the session
        sdict = settings_instance.get_dict()
        sn["settings_dict"] = sdict

        mh.set_language_from_settings(request)
        sp.content = "request.session: {}".format(dict(sn))
        sp.content += "\nSettings saved."

        # due to a unexpected behavior language is not changed in the first response
        # see https://stackoverflow.com/questions/52233911/django-languange-change-takes-effect-only-after-reload

    if hasattr(sp, "form"):
        sp.form.action_url_name = "settings_dialog"

    base = Container()
    endow_base_object(base, request)

    context = {"pagetype": "Settings-Form", "sp": sp, "base": base}
    return render(request, 'sober/main_settings_page.html', context)


def view_group_details(request, group_id):
    mh.set_language_from_settings(request)

    group = get_object_or_404(AuthGroup, pk=group_id)

    allowed_groups = mh.get_allowed_groups(request)

    if group not in allowed_groups:
        user = get_object_or_404(User, pk=request.user.pk)
        msg = _("You ({}) are not member of the group '{}'.".format(user.get_username(), group.name))
        raise PermissionDenied(msg)

    n_users = len(group.user_set.all())

    thesis_list1 = group.associated_bricks.filter(type=Brick.thesis)
    thesis_list2 = group.additional_bricks.filter(type=Brick.thesis)

    # concatenate the two lists and sort
    thesis_list = (thesis_list1 | thesis_list2).order_by("-update_datetime")

    base_object = Container()
    base_object.page_options = Container()
    base_object.page_options.page_type = "list_of_theses"
    base_object.page_options.special_head_link = "new_thesis_link"

    fargs = group.name, n_users, len(thesis_list)
    base_object.top_content = "Group: {}; Number of users: {}; number of Thesis: {}".format(*fargs)
    # !! hcl
    base_object.page_options.title = _("Overview of group '{}'".format(group.name))

    for tbrick in thesis_list:
        # trigger processing of the root of the respective trees (sufficient for the index)
        mh.BrickTree(tbrick, max_alevel=0)

    base_object.sorted_child_list = thesis_list

    # list of theses -> we can savely hardcode the bb_alevel to 0
    base_object.page_options.bb_alevel = 0

    endow_base_object(base_object, request)
    return render(request, 'sober/main_brick_tree.html', {'base': base_object})


class ViewMdPreview(View):
    """
    Render the plain txt-content of an url as markdown.
    Note: This has almost nothing to do with the actual purpose of this app.
    However the author has an use-case for this feature and abuses the available
    infrastructure.
    """

    # noinspection PyMethodMayBeStatic
    def get(self, request, url_id=None, strarg=None):

        if strarg is not None:
            return view_simple_page(request, "not_found")

        self.common(request)

        # hard-coded source urls for now:
        if url_id == 1:
            src_url = "https://pad.fsfw-dresden.de/p/funding-foss-35c3/export/txt"
        elif url_id == 2:
            src_url = "https://pad.totalism.org/p/hacc-naming-discussion/export/txt"
        else:
            return view_simple_page(request, "not_found")

        assert src_url.endswith("/export/txt")

        r = urllib.request.urlopen(src_url)
        src_txt = r.read().decode("utf8")

        # !! more security checks should take place here
        src_txt = src_txt.replace("script", "s-c-r-i-p-t")

        ctn = Container()
        ctn.src_txt = src_txt
        ctn.src_url = src_url.replace("/export/txt", "")
        ctn.a = 8

        base = Container()
        endow_base_object(base, request)

        context = {"ctn": ctn, "base": base}
        return render(request, 'sober/main_md_preview.html', context)

    def post(self, request):

        1/0

        base = Container()
        endow_base_object(base, request)

        context = {"base": base}
        return render(request, 'sober/main_md_preview.html', context)

    def common(self, request):
        mh.set_language_from_settings(request)


def endow_base_object(base_object, request):
    """
    Common functionality for all views, which render some toplevel template
    :param base_object:
    :param request:
    :return:
    """

    if not hasattr(base_object, "page_options"):
        base_object.page_options = Container()

    base_object.page_options.is_loggedin = request.user.is_authenticated

