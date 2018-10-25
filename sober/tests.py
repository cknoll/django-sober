from django.test import TestCase
from django.urls import reverse
from django.core import serializers
from django.conf import settings

from bs4 import BeautifulSoup

from . import model_helpers as mh

from ipydex import IPS
from .models import Brick, User, SettingsBunch

if __name__ == "__main__":
    print("Run tests with `python manage.py test sober.tests.T.ips`")

# todo: setup selenium:
# https://docs.djangoproject.com/en/2.1/topics/testing/tools/#django.test.LiveServerTestCase

# to get the current production data: ./manage.py dumpdata sober > sober_data.json


global_fixtures = ['sober_data2.json', 'aux_data.json']

default_brick_ordering = ['type', 'cached_avg_vote', 'update_datetime']


class DataIntegrityTests(TestCase):
    fixtures = global_fixtures

    def test_find_some_childs(self):

        try:
            brick = Brick.objects.get(pk=1)
        except Brick.DoesNotExist:
            success = False
        else:
            success = True

        self.assertTrue(success)

    def test_default_settings_are_not_assigned_to_user(self):

        default_settings = SettingsBunch.objects.get(pk=1)
        users = User.objects.all()

        self.assertNotEqual(len(users), 0)

        for user in users:
            self.assertIsNot(user.settings, default_settings)

    def test_settings_bunch_dict(self):

        default_settings = SettingsBunch.objects.get(pk=1)
        d = default_settings.get_dict()

        # actually here the concrete values are not important
        # we only want to have dict-access to them and they should be as expected
        self.assertEqual(d["language"], "en")
        self.assertEqual(d["max_rlevel"], 8)

    def test_child_type_lists(self):
        brick = Brick.objects.get(pk=1)

        bt = mh.BrickTree(brick, max_alevel=0)

        # test that the direct children are correctly assigned to direct access lists
        self.assertEqual(len(brick.direct_children_pro), 2)
        self.assertEqual(len(brick.direct_children_contra), 1)
        self.assertEqual(len(brick.direct_children_rest), 3)


class ViewTests(TestCase):
    fixtures = global_fixtures

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        # search html source for ":()" for variable name
        self.assertNotContains(response, "utc_required_variable:()")

        first_brick = response.context['base'].sorted_child_list[0]
        self.assertEqual(first_brick.title_tag, "Thesis#1")

        # utc = unit test comment
        self.assertNotContains(response, "utc_reaction_brick_drop_down_menu")

        self.assertContains(response, "utc_drop_down_menu_pro")
        self.assertContains(response, "utc_drop_down_menu_contra")
        self.assertContains(response, "utc_drop_down_menu_rest")

        # !! hcl
        self.assertContains(response, "Show Thesis and its Arguments")

    def test_bricktree1(self):

        response = self.client.get(reverse('show_brick', kwargs={"brick_id": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "utc_required_variable:()")  # search html source for ":()" for variable name

        self.assertContains(response, "reaction_brick_drop_down_menu")

        brick_list = response.context['base'].sorted_child_list
        b1 = brick_list[0]

        b1_childs = b1.children.all().order_by(*default_brick_ordering)
        b2 = b1_childs[0].children.all().order_by(*default_brick_ordering)[0]

        # test proper sorting of bricks (depth first)
        self.assertEqual(b1.type, Brick.thesis)
        self.assertEqual(b1_childs[0], brick_list[1])
        self.assertEqual(b2, brick_list[2])
        self.assertEqual(b1_childs[1], brick_list[3])

    def test_bricktree2(self):

        response = self.client.get(reverse('show_brick', kwargs={"brick_id": 2}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "utc_required_variable:()")  # search html source for ":()" for variable name

        # test to have an url_link to the parent
        link_text = '<a class="url_link" href="/b/{}">'.format(1)
        self.assertContains(response, link_text)

        # test to have an anchor_link to the level_1-child
        link_text = '<a class="anchor_link" href="#{}">'.format(2)
        self.assertContains(response, link_text)

    def test_new_brick_stage1(self):

        response = self.client.get(reverse('new_brick', kwargs={"brick_id": 1, "type_code": "pa"}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "utc_required_variable:()")  # search html source for ":()" for variable name

        # assert that the brick to react on is rendered
        # assert that a new brick is created and rendered after submitting the form
        # assert that the type and ml-classes are correct

    def test_new_brick_stage2(self):

        response1 = self.client.get(reverse('new_brick', kwargs={"brick_id": 1, "type_code": "pa"}))
        self.assertEqual(response1.status_code, 200)

        brick_id = response1.context['brick_id']
        type_code = response1.context['type_code']

        form, action_url = get_form_by_action_url(response1, "new_brick", brick_id=brick_id, type_code=type_code)
        self.assertIsNotNone(form)

        post_data = generate_post_data_for_form(form)

        response2 = self.client.post(action_url, post_data)
        self.assertEqual(response2.status_code, 200)
        self.assertNotContains(response2, "utc_required_variable:()")
        self.assertContains(response2, "utc_form_successfully_processed")

    def test_new_thesis_interaction(self):

        response = self.client.get(reverse('new_thesis',
                                           kwargs={"brick_id": -1, "type_code": "th"}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "utc_required_variable:()")  # search html source for ":()" for variable name

        # assert that no brick is rendered
        # assert that a new brick is created and rendered after submitting the form

    def test_edit_brick_stage1(self):

        response = self.client.get(reverse('edit_brick', kwargs={"brick_id": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "utc_required_variable:()")  # search html source for ":()" for variable name

    def test_edit_brick_stage2(self):

        response1 = self.client.get(reverse('edit_brick', kwargs={"brick_id": 2}))
        self.assertEqual(response1.status_code, 200)

        brick_id = response1.context['brick_id']

        form, action_url = get_form_by_action_url(response1, "edit_brick", brick_id=brick_id)
        self.assertIsNotNone(form)

        post_data = generate_post_data_for_form(form)

        response2 = self.client.post(action_url, post_data)

        self.assertEqual(response2.status_code, 200)
        self.assertNotContains(response2, "utc_required_variable:()")
        self.assertContains(response2, "utc_form_successfully_processed")

        # test to have an url_link to the parent
        link_text = '<a class="url_link" href="/b/{}">'.format(1)
        self.assertContains(response2, link_text)

        # test to have no anchor_link to the level_1-child
        link_text = '<a class="anchor_link" href='
        self.assertNotContains(response2, link_text)

        # assert that the the brick-fields have changed
        # assert that the update_time has changed but the creation_time has not

    def test_settings_dialog(self):

        original_data = serializers.serialize("json", SettingsBunch.objects.all())
        response1 = self.client.get(reverse('settings_dialog'))
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, "utc_english_language_enabled")

        settings_dict = self.client.session.get("settings_dict")
        self.assertIsNone(settings_dict)

        form, action_url = get_form_by_action_url(response1, "settings_dialog")
        post_data = generate_post_data_for_form(form, spec_values={"language": "de", "max_rlevel": 21})
        response2 = self.client.post(action_url, post_data)
        self.assertContains(response2, "utc_deutsche_sprache_aktiviert")

        settings_dict = self.client.session.get("settings_dict")

        self.assertIsNotNone(settings_dict)
        self.assertEqual(settings_dict["language"], "de")
        self.assertEqual(settings_dict["max_rlevel"], 21)

        new_data = serializers.serialize("json", SettingsBunch.objects.all())

        # database must not have changed
        self.assertEqual(original_data, new_data)

    def test_vote_criterion(self):

        response1 = self.client.get(reverse('thesis_list'))
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, "utc_english_language_enabled")

        # test the occurrence of the different vote-criteria
        # if the wording of the vote-criterion changes this has to change as well

        self.assertContains(response1, "Agreement")

        response2 = self.client.get(reverse('show_brick', kwargs={"brick_id": 1}))
        self.assertContains(response2, "Agreement")
        self.assertContains(response2, "Cogency")
        self.assertContains(response2, "Relevance")

    def test_debug_view(self):
        response1 = self.client.get(reverse('debug_page'))
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, "utc_debug_page")

        # default value is False for unittests
        self.assertFalse(settings.DEBUG)
        self.assertContains(response1, "utc_settings.DEBUG=False")

        settings.DEBUG = True
        response2 = self.client.get(reverse('debug_page'))
        self.assertContains(response2, "utc_settings.DEBUG=True")

        # restore the original value (this is not done automatically)
        settings.DEBUG = False

    # noinspection PyMethodMayBeStatic
    def test_start_ips(self):
        if 1:
            # brick = Brick.objects.get(pk=1)

            from django.contrib.auth import views as auth_views
            lv = auth_views.LoginView
            IPS()
        else:
            print("Omitting debug tool IPS")


# ------------------------------------------------------------------------
# below live some aliases to quickly access specific tests
# ------------------------------------------------------------------------

# run shortcut: py3 manage.py test sober.tests.T.ips

T = ViewTests
T.a = T.test_settings_dialog
T.ips = T.test_start_ips

# ------------------------------------------------------------------------
# below lives auxiliary code which is related to testing but does not contain tests
# ------------------------------------------------------------------------


def get_form_by_action_url(response, url_name, **url_name_kwargs):
    """
    Auxiliary function that returns a bs-object of the form which is specifies by action-url.

    Also return action_url

    :param response:
    :param url_name:
    :param url_name_kwargs:
    :return:
    """
    bs = BeautifulSoup(response.content, 'html.parser')
    action_url = reverse(url_name, kwargs=url_name_kwargs)
    forms = bs.find_all("form")

    for form in forms:
        if form.attrs['action'] == action_url:
            return form, action_url

    return None, action_url


def get_form_fields_to_submit(form):
    """
    Return two lists: fields and hidden_fields.

    :param form:
    :return:
    """

    inputs = form.find_all("input")
    textareas = form.find_all("textarea")

    post_fields = inputs + textareas

    types_to_omit = ["submit", "cancel"]

    fields = []
    hidden_fields = []
    for field in post_fields:
        ftype = field.attrs.get("type")
        if ftype in types_to_omit:
            continue

        if ftype == "hidden":
            hidden_fields.append(field)
        else:
            fields.append(field)

    return fields, hidden_fields


def generate_post_data_for_form(form, default_value="xyz", spec_values=None):
    """
    Return a dict containing all dummy-data for the form

    :param form:
    :param default_value:   str; use this value for all not specified fields
    :param spec_values:     dict; use these values to override default value

    :return:                dict of post_data
    """

    if spec_values is None:
        spec_values = {}

    fields, hidden_fields = get_form_fields_to_submit(form)

    post_data = {}
    for f in hidden_fields:
        post_data[f.attrs['name']] = f.attrs['value']

    for f in fields:
        post_data[f.attrs['name']] = default_value

    post_data.update(spec_values)

    return post_data




