from django.test import TestCase
from django.urls import reverse

from bs4 import BeautifulSoup

from ipydex import IPS

from .models import Brick


# todo: setup selenium:
# https://docs.djangoproject.com/en/2.1/topics/testing/tools/#django.test.LiveServerTestCase

# to get the current production data: ./manage.py dumpdata sober_app > sober_data.json


global_fixtures = ['sober_data2.json', 'sbunch.json']


class SoberModelTests1(TestCase):
    fixtures = global_fixtures

    def test_find_some_childs(self):

        try:
            brick = Brick.objects.get(pk=1)
        except Brick.DoesNotExist:
            success = False
        else:
            success = True

        self.assertTrue(success)


class SoberViewTests(TestCase):
    fixtures = global_fixtures

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "utc_required_variable:()")  # search html source for ":()" for variable name

        first_brick = response.context['base'].sorted_child_list[0]
        self.assertEqual(first_brick.title_tag, "Thesis#1")

        # utc = unit test comment
        self.assertNotContains(response, "utc_reaction_brick_drop_down_menu")

        # !! hcl
        self.assertContains(response, "Show Thesis and its Arguments")

    def test_bricktree1(self):

        response = self.client.get(reverse('brickid', kwargs={"brick_id": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "utc_required_variable:()")  # search html source for ":()" for variable name

        self.assertContains(response, "reaction_brick_drop_down_menu")

        brick_list = response.context['base'].sorted_child_list
        b1 = brick_list[0]

        b1_childs = b1.children.all()

        # test proper sorting of bricks (depth first)
        self.assertEqual(b1.type, Brick.thesis)
        self.assertEqual(b1_childs[0], brick_list[1])
        self.assertEqual(b1_childs[0].children.all()[0], brick_list[2])
        self.assertEqual(b1_childs[1], brick_list[3])

    def test_bricktree2(self):

        response = self.client.get(reverse('brickid', kwargs={"brick_id": 2}))
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

        response1 = self.client.get(reverse('settings_dialog'))
        self.assertEqual(response1.status_code, 200)


# ------------------------------------------------------------------------
# below live some aliases to quickly access specific tests
# ------------------------------------------------------------------------

# run shortcut: py3 manage.py test sober_app.tests.T.a

T = SoberViewTests
T.a = T.test_settings_dialog

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


def generate_post_data_for_form(form, default_value="xyz"):
    """
    Return a dict containing all dummy-data for the form

    :param form:
    :param default_value:
    :return:
    """

    fields, hidden_fields = get_form_fields_to_submit(form)

    post_data = {}
    for f in hidden_fields:
        post_data[f.attrs['name']] = f.attrs['value']

    for f in fields:
        post_data[f.attrs['name']] = default_value

    return post_data




