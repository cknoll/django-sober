import sys
from django.forms import ModelForm, EmailField
from django.core.exceptions import FieldDoesNotExist
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from sober.models import Brick, SettingsBunch, Vote, Feedback

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
        try:
            maxlength = model._meta.get_field(fn).max_length
            res[fn] = "Maxlength = {}".format(maxlength)
        except FieldDoesNotExist:
            pass
    return res


# almost empty object to store some attributes at runtime
# this mechanism serves to use flexible relative imports:
# add all ModelForms
# TODO: Remove due to obsolescence
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
    captcha = CaptchaField()
    class Meta:
        model = Brick
        fields = ['title', 'content', 'references', 'tags', "associated_group",
                  "allowed_for_additional_groups"]
        help_texts = create_help_texts(model, fields)

    def __init__(self, *args, **kwargs):
        # A new form should remove the irrelevant group fields if it does not explicitly belong to a thesis
        kgf = kwargs.pop("keep_group_fields", None)
        allowed_groups = kwargs.pop("allowed_groups", None)

        if not allowed_groups:
            # !!hcl
            errmsg = "At least one allowed group is necessary to create the form.\n"\
                     "The current user (inluding anonymous) seems to be in no group.\n"\
                     "This should be handled in the caller."
            raise ValueError(errmsg)

        super().__init__(*args, **kwargs)

        self.fields["associated_group"].queryset = allowed_groups
        self.fields["allowed_for_additional_groups"].queryset = allowed_groups
        self.fields["allowed_for_additional_groups"].required = False

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


class SignUpForm(UserCreationForm):
    email = EmailField(required=True, help_text=_("not yet used"))
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        # help_texts = {"email": "not yet used"}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class FeedbackForm(ModelForm):
    email = EmailField(required=False, help_text=_("optionally"))
    captcha = CaptchaField()

    class Meta:
        model = Feedback
        fields = ("email", "content")

    def save(self, commit=False):
        if commit:
            raise ValueError("We currently do not want to save feedback.")
        return self.cleaned_data
