"""
source: https://gist.github.com/c00kiemon5ter/7806c1eac8c6a3e82f061ec32a55c702

todo:  !! find out about licence


Extend createsuperuser command to allow non-interactive creation of a
superuser with a password.

Instructions:

  mkdir -p path-to-your-app/management/commands/
  touch path-to-your-app/management/__init__.py
  touch path-to-your-app/management/commands/__init__.py

and place this file under path-to-your-app/management/commands/

Example usage:

  manage.py create-superuser \
          --username foo     \
          --password foo     \
          --email foo@foo.foo
"""
from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError


class Command(createsuperuser.Command):
    help = "Create a superuser with a password non-interactively"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--password",
            dest="password",
            default=None,
            help="Specifies the password for the superuser.",
        )

    def handle(self, *args, **options):
        options.setdefault("interactive", False)
        database = options.get("database")
        password = options.get("password")
        username = options.get("username")
        email = options.get("email")

        if not password or not username or not email:
            raise CommandError("--email --username and --password are required options")

        user_data = {
            "username": username,
            "password": password,
            "email": email,
        }

        self.UserModel._default_manager.db_manager(database).create_superuser(**user_data)

        if options.get("verbosity", 0) >= 1:
            self.stdout.write("Superuser created successfully.")
