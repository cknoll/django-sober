# Generated by Django 2.1 on 2018-08-08 13:21

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField(max_length=5000)),
                ('tags', models.CharField(max_length=1000)),
                ('datetime', models.DateTimeField()),
                ('type', models.SmallIntegerField(choices=[(1, 'Thesis'), (2, 'Pro'), (3, 'Contra'), (4, 'Comment'), (5, 'Question')])),
                ('allowed_for_groups', models.ManyToManyField(to='auth.Group')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='sober_app.Brick')),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=5000)),
                ('brick', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sober_app.Brick')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('settings', models.TextField(max_length=5000)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
                ('brick', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sober_app.Brick')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sober_app.User')),
            ],
        ),
        migrations.AddField(
            model_name='complaint',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sober_app.User'),
        ),
    ]
