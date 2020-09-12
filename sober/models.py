from django.db import models
from django.utils import timezone
from collections import OrderedDict
from django.contrib.auth.models import User, Group as AuthGroup
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db.models.signals import post_save
from django.dispatch import receiver

# see https://docs.djangoproject.com/en/2.1/ref/models/fields/


class SettingsBunch(models.Model):

    supported_languages = [("en", "English"), ("de", "German"), ("es", "Spanish")]
    language = models.CharField(default="en", max_length=10, choices=supported_languages)

    # maximum relative level to show of a brick_tree
    max_rlevel = models.SmallIntegerField(default=8,
                                          verbose_name=_("Maximum relative level to display"))

    def get_dict(self):
        """
        Generate a python dict for all fields. This will be saved in the http-session.
        :return:    resulting dict
        """

        # noinspection PyUnresolvedReferences
        fieldnames = [f.name for f in self._meta.fields]
        fieldnames.remove("id")

        res = {}
        for fn in fieldnames:
            res[fn] = getattr(self, fn)

        return res


# https://docs.djangoproject.com/en/2.1/topics/auth/default/#how-to-log-a-user-in
# https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html
class SoberUser(models.Model):
    """
    auth.User is used for authentification. However, to store additional user related Information
    we use this one-to-one relationship with hooks.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # add a storage for settings
    settings = models.ForeignKey(SettingsBunch, null=True, on_delete=models.SET_NULL)


@receiver(post_save, sender=User)
def create_soberuser(sender, instance, created, **kwargs):
    if created:
        # noinspection PyUnresolvedReferences
        SoberUser.objects.create(user=instance)
        # !! TODO: Add test to verify that new user can see and edit public bricks
        instance.groups.add(AuthGroup.objects.get(name='public'))


@receiver(post_save, sender=User)
def save_soberuser(sender, instance, **kwargs):
    instance.soberuser.save()

# end of SoberUser


class SoberGroup(models.Model):
    """
    auth.Group has not all fields which we want.
    We extend that auth.Group, the same way we did with auth.User
    """
    group = models.OneToOneField(AuthGroup, on_delete=models.CASCADE)
    description = models.TextField(max_length=5000, default="")
    admins = models.ManyToManyField(User, blank=True)

    # Note: There was a strange exception when trying to similar hooks like
    # for SoberUser above. Creating and Changing through admin-interface
    # nevertheless works


class Brick(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=5000)  # max_length for security
    tags = models.CharField(null=True, max_length=1000)
    creation_datetime = models.DateTimeField(default=timezone.now)
    update_datetime = models.DateTimeField(default=timezone.now)

    references = models.TextField(null=True, max_length=5000)

    thesis = 1
    pro = 2
    contra = 3
    comment = 4
    question = 5
    improvement = 6
    # !! add improvement suggestion

    symbol_mapping = {thesis: "!",
                      pro: "✓",
                      contra: "⚡",
                      question: "?",
                      comment: '&#x1f5e8;',
                      improvement: '&#x1f4a1;',  # :bulb:
                      }

    type_names_codes = \
            [(thesis, "Thesis", "th"),
             (pro, "Pro", "pa"),
             (contra, "Contra", "ca"),
             (comment, "Comment", "co"),
             (question, "Question", "qu"),
             (improvement, "Improvement", "is"),
            ]

    types = [(id, name) for id, name, _ in type_names_codes]

    # !! it would have been better to use the 2char-typecode instead of ints as db-entry
    type = models.SmallIntegerField(choices=types)
    # for convenient external access
    types_map = OrderedDict(types)

    # different order for different map
    typecode_map = OrderedDict([(code, id) for id, name, code in type_names_codes])
    reverse_typecode_map = OrderedDict([(id, code) for id, name, code in type_names_codes])

    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='children', on_delete=models.SET_NULL)

    associated_group = models.ForeignKey(AuthGroup, on_delete=models.CASCADE, default=1,
                                         related_name="associated_bricks")
    allowed_for_additional_groups = models.ManyToManyField(AuthGroup, related_name="additional_bricks")

    cached_avg_vote = models.FloatField(default=0)
    creation_user = models.ForeignKey(User, null=True,
                                      related_name='created_bricks', on_delete=models.SET_NULL)

    # end of class variables

    def __init__(self, *args, **kwargs):
        """explicitly define a constructor to get default values for instance attributes"""
        super().__init__(*args, **kwargs)

        # this flag indicates whether the current brick is "contra" its direct parent (necessary for visualization)
        # in the future there might be more possibilities for this flag, apart of just type==contra
        self.negation_flag = self.type in (self.contra, )

        # cummulated negation flag (will by set by a function)
        self.cnegflag = None


    def get_short_title(self, n_chars=30):
        assert n_chars > 3
        assert isinstance(n_chars, int)
        short_title = self.title
        # noinspection PyTypeChecker
        if len(short_title) > n_chars:
            short_title = "{}...".format(short_title[:n_chars-3])

        return short_title

    def get_vote_criterion(self):
        vc_map = {self.thesis: _("Agreement"),
                  self.pro: _("Cogency"),
                  self.contra: _("Cogency"),
                  self.comment: _("Relevance"),
                  self.question: _("Relevance"),
                  self.improvement: _("Relevance"),
                 }

        return vc_map[int(self.type)]

    def get_symbol(self):
        return self.symbol_mapping[int(self.type)]

    def get_root_parent(self):
        """
        Go upward in child-parent-hierarchy and return that parent-...-parent brick which
        has no parent itself. Also return the number of upward-steps.

        :return: root-parent-brick, upward_steps
        """

        brick = self

        level = 0
        while brick.parent is not None:
            # for performance reasons this might be cached
            brick = brick.parent
            level += 1

        assert brick.parent is None
        return brick, level

    def get_hyper_parent(self):
        """
        Return the uppermost parent (if settings do not forbid this)
        :return:
        """
        # TODO: take care for maximum level settings here (`show in context` use case)
        # (not yet finished)

        rootparent, level = self.get_root_parent()
        return rootparent

    def __str__(self):
        short_title = self.get_short_title()

        return "Brick_{}({}): '{}'".format(self.pk, self.types_map[self.type], short_title)

# ensure data consistency
assert len(Brick.symbol_mapping) == len(Brick.type_names_codes)


class Vote(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    brick = models.ForeignKey(Brick, null=True, on_delete=models.SET_NULL)
    value = models.FloatField(default=0, validators=[MinValueValidator(-2), MaxValueValidator(2)])

    # make min and max easier accessible
    min = value.validators[0].limit_value
    max = value.validators[1].limit_value


class Complaint(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    brick = models.ForeignKey(Brick, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=5000)


class Feedback(models.Model):
    """
    Currently no Feedback-object is stored in the database.
    This model serves for easily generating a form.
    """
    content = models.TextField(max_length=5000)
