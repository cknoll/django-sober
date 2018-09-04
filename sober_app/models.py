from django.db import models
from django.utils import timezone
from collections import OrderedDict
from django.contrib.auth.models import User as djUser, Group


# see https://docs.djangoproject.com/en/2.1/ref/models/fields/


# https://docs.djangoproject.com/en/2.1/topics/auth/default/#how-to-log-a-user-in
class User(djUser):
    # add a storage for settings
    settings = models.TextField(max_length=5000)  # assume that it will be json data


class Brick(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=5000)  # max_length for security
    tags = models.CharField(null=True, max_length=1000)
    creation_datetime = models.DateTimeField(default=timezone.now)
    update_datetime = models.DateTimeField(default=timezone.now)

    references = models.CharField(null=True, max_length=1000)

    thesis = 1
    pro = 2
    contra = 3
    comment = 4
    question = 5
    # !! add improvement suggestion

    type_names_codes = \
            [(thesis, "Thesis", "th"),
             (pro, "Pro", "pa"),
             (contra, "Contra", "ca"),
             (comment, "Comment", "co"),
             (question, "Question", "qu"),
            ]

    types = [(id, name) for id, name, _ in type_names_codes]
    type = models.SmallIntegerField(choices=types)
    # for convenient external access
    types_map = OrderedDict(types)

    # different order for different map
    typecode_map = OrderedDict([(code, id) for id, name, code in type_names_codes])
    reverse_typecode_map = OrderedDict([(id, code) for id, name, code in type_names_codes])

    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='children', on_delete=models.SET_NULL)

    allowed_for_groups = models.ManyToManyField(Group)

    cached_avg_vote = models.FloatField(default=0)
    creation_user = models.ForeignKey(User, null=True,
                                      related_name='created_bricks', on_delete=models.SET_NULL)

    def __str__(self):
        short_title = self.title
        if len(short_title) > 40:
            short_title = "{}...".format(short_title[:17])

        return "Brick_{}({}): '{}'".format(self.pk, self.types_map[self.type], short_title)


class Vote(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    brick = models.ForeignKey(Brick, null=True, on_delete=models.SET_NULL)
    value = models.FloatField()


class Complaint(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    brick = models.ForeignKey(Brick, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=5000)


