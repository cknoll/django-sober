from django.test import TestCase
from django.urls import reverse

from ipydex import IPS

from .models import Brick


# todo: setup selenium:
# https://docs.djangoproject.com/en/2.1/topics/testing/tools/#django.test.LiveServerTestCase

# to get the current production data: ./manage.py dumpdata sober_app > sober_data.json


global_fixtures = ['sober_data2.json']


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
        first_brick = response.context['base'].sorted_child_list[0]
        self.assertEqual(first_brick.title_tag, "Thesis#1")

    def test_bricktree(self):

        response = self.client.get(reverse('brickid', kwargs={"brick_id": 1}))
        self.assertEqual(response.status_code, 200)

        brick_list = response.context['base'].sorted_child_list
        b1 = brick_list[0]

        b1_childs = b1.children.all()

        # test proper sorting of bricks (depth first)
        self.assertEqual(b1.type, Brick.thesis)
        self.assertEqual(b1_childs[0], brick_list[1])
        self.assertEqual(b1_childs[0].children.all()[0], brick_list[2])
        self.assertEqual(b1_childs[1], brick_list[3])

    def test_new_brick_interaction(self):

        response = self.client.get(reverse('new_brick', kwargs={"brick_id": 1, "type_code": "pa"}))
        self.assertEqual(response.status_code, 200)

        # assert that the brick to react on is rendered
        # assert that a new brick is created and rendered after submitting the form
        # assert that the type and ml-classes are correct

    def test_new_thesis_interaction(self):

        response = self.client.get(reverse('new_thesis',
                                           kwargs={"brick_id": -1, "type_code": "th"}))
        self.assertEqual(response.status_code, 200)

        # assert that no brick is rendered
        # assert that a new brick is created and rendered after submitting the form

    def test_edit_brick_interaction(self):

        response = self.client.get(reverse('edit_brick', kwargs={"brick_id": 1}))
        self.assertEqual(response.status_code, 200)

        # assert that the the brick-fields can be changed
        # assert that the update_time changes but the creation_time does not
