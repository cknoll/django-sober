import sys
from django.forms import ModelForm
from sober.models import Brick, SettingsBunch, Vote

from ipydex import IPS

# ------------------------------------------------------------------------
# first some auxiliary code related to forms
# ------------------------------------------------------------------------


def create_help_texts(model, fieldnames):
    """
    Automatically extract maximum length form the model

    :param model:
    :param fieldnames:
    :return:
    """
    res = {}
    for fn in fieldnames:
        # noinspection PyProtectedMember
        # maxlength = model._field_dict[fn].max_length
        maxlength = model._meta.get_field(fn).max_length
        res[fn] = "Maxlength = {}".format(maxlength)
    return res


# almost empty object to store some attributes at runtime
# this mechanism serves to use flexible relative imports:
# add all ModelForms
class FormContainer(object):
    def __init__(self):
        mod = sys.modules[__name__]
        for key, value in mod.__dict__.items():
            if isinstance(value, type) and issubclass(value, ModelForm):
                self.__dict__[key] = value

# ------------------------------------------------------------------------
# below live the actual forms
# ------------------------------------------------------------------------


class BrickForm(ModelForm):
    class Meta:
        model = Brick
        fields = ['title', 'content', 'references', 'tags', "associated_group",
                  "allowed_for_additional_groups"]
        help_texts = create_help_texts(model, fields)

    def __init__(self, *args, **kwargs):
        # A new form should remove the irrelevant group fields if it does not explicitly belong to a thesis
        kgf = kwargs.pop("keep_group_fields", None)
        super().__init__(*args, **kwargs)

        self.fields["allowed_for_additional_groups"].required=False

        try:
            the_type = kwargs.get("instance").type
        except AttributeError:
            the_type = None

        # evalueate the type if the kgf flag was not specified
        if kgf is None and the_type == Brick.thesis:
            kgf = True

        if not kgf:
            self._remove_irrelevant_fields()

    def _remove_irrelevant_fields(self):
        """
        BrickForms which do not belong to a thesis should not contain the fields
        `associated_group` and `allowed_for_additional_groups`.
        Reason: their group is defined by the thesis to which they belong

        :return:
        """

        fields_to_delete = ["associated_group", "allowed_for_additional_groups"]

        # self.fields is as ordered dict
        for f in fields_to_delete:
            self.fields.pop(f)


class SettingsForm(ModelForm):
    class Meta:
        model = SettingsBunch
        fields = ['language', 'max_rlevel']
        help_texts = create_help_texts(model, fields)


class VoteForm(ModelForm):
    class Meta:
        model = Vote
        fields = ["value"]
        # brick will be a hidden field
        # user will be set by the server from the session

    def slider_data(self):
        # note: self.fields is an OrderedDict
        slider_key = list(self.fields.keys())[0]
        return {"key": slider_key,
                "default_value": self.instance.value,
                "min": Vote.min,
                "max": Vote.max}


# add all forms to the container which allows simple and clean relative imports
forms = FormContainer()
