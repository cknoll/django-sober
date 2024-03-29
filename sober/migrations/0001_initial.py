# Generated by Django 2.1.1 on 2019-03-20 18:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth", "0009_alter_user_last_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Brick",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField(max_length=5000)),
                ("tags", models.CharField(max_length=1000, null=True)),
                ("creation_datetime", models.DateTimeField(default=django.utils.timezone.now)),
                ("update_datetime", models.DateTimeField(default=django.utils.timezone.now)),
                ("references", models.TextField(max_length=5000, null=True)),
                (
                    "type",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Thesis"),
                            (2, "Pro"),
                            (3, "Contra"),
                            (4, "Comment"),
                            (5, "Question"),
                            (6, "Improvement"),
                        ]
                    ),
                ),
                ("cached_avg_vote", models.FloatField(default=0)),
                (
                    "allowed_for_additional_groups",
                    models.ManyToManyField(related_name="additional_bricks", to="auth.Group"),
                ),
                (
                    "associated_group",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="associated_bricks",
                        to="auth.Group",
                    ),
                ),
                (
                    "creation_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_bricks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="sober.Brick",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Complaint",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("content", models.TextField(max_length=5000)),
                (
                    "brick",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to="sober.Brick"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("content", models.TextField(max_length=5000)),
            ],
        ),
        migrations.CreateModel(
            name="SettingsBunch",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        choices=[("en", "English"), ("de", "German"), ("es", "Spanish")],
                        default="en",
                        max_length=10,
                    ),
                ),
                (
                    "max_rlevel",
                    models.SmallIntegerField(
                        default=8, verbose_name="Maximum relative level to display"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SoberGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("description", models.TextField(default="", max_length=5000)),
                ("admins", models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                (
                    "group",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="auth.Group"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SoberUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "settings",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="sober.SettingsBunch",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Vote",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "value",
                    models.FloatField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(-2),
                            django.core.validators.MaxValueValidator(2),
                        ],
                    ),
                ),
                (
                    "brick",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, to="sober.Brick"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
