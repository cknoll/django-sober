from django.test import TestCase

from .models import Brick

# to get the current production data: ./manage.py dumpdata sober_app > sober_data.json


class SoberModelTests1(TestCase):
    fixtures = ['sober_data.json']

    def test_find_some_childs(self):

        try:
            brick = Brick.objects.get(pk=1)
        except Brick.DoesNotExist:
            success = False
        else:
            success = True

        self.assertTrue(success)
