from django.db import models
# see https://docs.djangoproject.com/en/2.1/ref/models/fields/


from django.contrib.auth.models import User as djUser, Group


# https://docs.djangoproject.com/en/2.1/topics/auth/default/#how-to-log-a-user-in
class User(djUser):
    # add a storage for settings
    settings = models.TextField(max_length=5000)  # assume that it will be json data


class Brick(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=5000)  # max_length for security
    tags = models.CharField(max_length=1000)
    datetime = models.DateTimeField()

    thesis = 1
    pro = 2
    contra = 3
    comment = 4
    question = 5

    types = [(thesis, "Thesis"),
             (pro, "Pro"),
             (contra, "Contra"),
             (comment, "Comment"),
             (question, "Question")
            ]

    type = models.SmallIntegerField(choices=types)

    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='children', on_delete=models.SET_NULL)

    allowed_for_groups = models.ManyToManyField(Group)


class Vote(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    brick = models.ForeignKey(Brick, null=True, on_delete=models.SET_NULL)
    value = models.FloatField()


class Complaint(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    brick = models.ForeignKey(Brick, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=5000)


