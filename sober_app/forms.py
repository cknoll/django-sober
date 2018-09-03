import sys
from django.forms import ModelForm
from sober_app.models import Brick


# empty object to store some attributes at runtime
# this mechanism serves to use flexible relative imports:
# add all ModelForms
class FormContainer(object):
    def __init__(self):
        mod = sys.modules[__name__]
        for key, value in mod.__dict__.items():
            if isinstance(value, type) and issubclass(value, ModelForm):
                self.__dict__[key] = value


# Create the form class.
class BrickForm(ModelForm):
    class Meta:
        model = Brick
        fields = ['title', 'content', 'references', 'tags']


forms = FormContainer()
