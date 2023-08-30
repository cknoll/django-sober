import time
import os
import secrets
import re
import os
from os.path import join as pjoin

# these packages are not in requirements.txt but in deployment_requirements.txt
# noinspection PyUnresolvedReferences
from packaging import version
# noinspection PyUnresolvedReferences
from ipydex import IPS, activate_ips_on_exception

min_du_version = version.parse("0.3.0")
try:
    # this is not listed in the requirements because it is not needed on the deployment server
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import deploymentutils as du

    vsn = version.parse(du.__version__)
    if vsn < min_du_version:
        print(f"You need to install `deploymentutils` in version {min_du_version} or later. Quit.")
        exit()


except ImportError as err:
    print("You need to install the package `deploymentutils` to run this script.")


"""
This script serves to deploy and maintain the django app `moodpoll` on an uberspace account.
It is largely based on this tutorial: <https://lab.uberspace.de/guide_django.html>.
"""

# call this before running the script:
# eval $(ssh-agent); ssh-add -t 10m


workdir = os.path.abspath(os.getcwd())
msg = (
       "This deployment script is expected to be run from the BASEDIR of the django project, i.e. "
       "from the same directory where manage.py is located. This seems not to be the case.\n"
       f"Your current workdir is {workdir}"
)

if not os.path.isfile(pjoin(workdir, "manage.py")):
    raise FileNotFoundError(msg)

# simplify debugging
activate_ips_on_exception()


# -------------------------- Essential Config section  ------------------------

config = du.get_nearest_config("config.toml")


remote = config("dep::remote")
user = config("dep::user")

# -------------------------- Begin Optional Config section -------------------------
# if you know what you are doing you can adapt these settings to your needs

# this is the root dir of the project (where setup.py lies)
# if you maintain more than one instance (and deploy.py lives outside the project dir, this has to change)
project_src_path = os.path.dirname(du.get_dir_of_this_file())
assert os.path.isfile(os.path.join(project_src_path, "manage.py"))

# directory for deployment files (e.g. database files)
app_name = config("dep::app_name")
project_name = config("dep::PROJECT_NAME")

# TIME_ZONE = config("dep::TIME_ZONE")




# this is needed to distinguish different django instances on the same uberspace account
port = config("dep::port")
django_url_prefix = config("dep::django_url_prefix")
static_url_prefix = config("dep::static_url_prefix")


asset_dir = pjoin(du.get_dir_of_this_file(), "files")  # contains the templates
temp_workdir = pjoin(du.get_dir_of_this_file(), "tmp_workdir")  # this will be deleted/overwritten

# -------------------------- End Config section -----------------------

# it should not be necessary to change the data below, but it might be interesting what happens.
# (After all, this code runs on your computer/server under your responsibility).


# name of the directory for the virtual environment:
venv = config("dep::venv")
venv_path = f"/home/{user}/{venv}"

# because uberspace offers many python versions:
pipc = config("dep::pip_command")
python_version = config("dep::python_version")



du.argparser.add_argument("-o", "--omit-tests", help="omit test execution (e.g. for dev branches)", action="store_true")
du.argparser.add_argument("-d", "--omit-database",
                          help="omit database-related-stuff (and requirements)", action="store_true")
du.argparser.add_argument("-s", "--omit-static", help="omit static file handling", action="store_true")
du.argparser.add_argument("-x", "--omit-backup",
                          help="omit db-backup (avoid problems with changed models)", action="store_true")
du.argparser.add_argument(
    "-q",
    "--omit-requirements",
    action="store_true",
    help="do not install requirements (allows to speed up deployment)",
)
du.argparser.add_argument("-p", "--purge", help="purge target directory before deploying", action="store_true")
du.argparser.add_argument("--debug", help="start debug interactive mode (IPS), then exit", action="store_true")

args = du.parse_args()

final_msg = f"Deployment script {du.bgreen('done')}."



if args.target == "remote":
    # this is where the code will live after deployment
    target_deployment_path = config("dep::deployment_path")
    static_root_dir = f"{target_deployment_path}/collected_static"
    debug_mode = False

    # todo: read this from config
    allowed_hosts = [f"{user}.uber.space"]
else:
    raise NotImplementedError("local deployment is not supported by this script")


# TODO: review
init_fixture_path = os.path.join(target_deployment_path, "apps/quiz/fixtures/real_quiz_data.json")




# print a warning for data destruction
du.warn_user(
    app_name,
    args.target,
    args.unsafe,
    deployment_path=target_deployment_path,
    user=user,
    host=remote,
)


# ensure clean workdir
os.system(f"rm -rf {temp_workdir}")
os.makedirs(temp_workdir)

c = du.StateConnection(remote, user=user, target=args.target)


def create_and_setup_venv(c):


    # TODO: check if venv exists

    c.run(f"{pipc} install --user virtualenv")

    print("create and activate a virtual environment inside $HOME")
    c.chdir("~")

    c.run(f"rm -rf {venv}")
    c.run(f"{python_version} -m virtualenv -p {python_version} {venv}")

    c.activate_venv(f"~/{venv}/bin/activate")

    c.run(f"pip install --upgrade pip")
    c.run(f"pip install --upgrade setuptools")

    print("\n", "install uwsgi", "\n")
    c.run(f"pip install uwsgi")

    # ensure that the same version of deploymentutils like on the controller-pc is also in the server
    c.deploy_this_package()


def render_and_upload_config_files(c):

    c.activate_venv(f"~/{venv}/bin/activate")

    # generate the general uwsgi ini-file
    tmpl_dir = os.path.join("uberspace", "etc", "services.d")
    tmpl_name = "template_PROJECT_NAME_uwsgi.ini"
    target_name = "PROJECT_NAME_uwsgi.ini".replace("PROJECT_NAME", project_name)
    du.render_template(
        tmpl_path=pjoin(asset_dir, tmpl_dir, tmpl_name),
        target_path=pjoin(temp_workdir, tmpl_dir, target_name),
        context=dict(venv_abs_bin_path=f"{venv_path}/bin/", project_name=project_name),
    )

    # generate config file for django uwsgi-app
    tmpl_dir = pjoin("uberspace", "uwsgi", "apps-enabled")
    tmpl_name = "template_PROJECT_NAME.ini"
    target_name = "PROJECT_NAME.ini".replace("PROJECT_NAME", project_name)
    du.render_template(
        tmpl_path=pjoin(asset_dir, tmpl_dir, tmpl_name),
        target_path=pjoin(temp_workdir, tmpl_dir, target_name),
        context=dict(
            venv_dir=f"{venv_path}", deployment_path=target_deployment_path, port=port, user=user
        ),
    )

    #
    # ## upload config files to remote $HOME ##
    #
    srcpath1 = os.path.join(temp_workdir, "uberspace")
    filters = "--exclude='**/README.md' --exclude='**/template_*'"  # not necessary but harmless
    c.rsync_upload(srcpath1 + "/", "~", filters=filters, target_spec="remote")


def update_supervisorctl(c):

    c.activate_venv(f"~/{venv}/bin/activate")

    c.run("supervisorctl reread", target_spec="remote")
    c.run("supervisorctl update", target_spec="remote")
    print("waiting 10s for uwsgi to start")
    time.sleep(10)

    res1 = c.run("supervisorctl status", target_spec="remote")

    assert "uwsgi" in res1.stdout
    assert "RUNNING" in res1.stdout


def set_web_backend(c):
    c.activate_venv(f"~/{venv}/bin/activate")

    c.run(
        f"uberspace web backend set {django_url_prefix} --http --port {port}", target_spec="remote"
    )

    # note 1: the static files which are used by django are served under '{static_url_prefix}'/
    # (not {django_url_prefix}}{static_url_prefix})
    # they are served by apache from ~/html{static_url_prefix}, e.g. ~/html/markpad1-static

    c.run(f"uberspace web backend set {static_url_prefix} --apache", target_spec="remote")




def upload_files(c):
    print("\n", "ensure that deployment path exists", "\n")
    c.run(f"mkdir -p {target_deployment_path}", target_spec="both")

    c.activate_venv(f"~/{venv}/bin/activate")

    print("\n", "upload config file", "\n")
    c.rsync_upload(config.path, target_deployment_path, target_spec="remote")

    c.chdir(target_deployment_path)

    print("\n", "upload current application files for deployment", "\n")
    # omit irrelevant files (like .git)
    # TODO: this should be done more elegantly

    db_file_name = os.path.split(config('dep::DB_FILE_PATH'))[-1]
    filters = f"--exclude='.git/' --exclude='.idea/' --exclude='{db_file_name}' "

    c.rsync_upload(
        project_src_path + "/", target_deployment_path, filters=filters, target_spec="both"
    )

    c.run(f"touch requirements.txt", target_spec="remote")


def purge_deployment_dir(c):
    if not args.omit_backup:
        print(
            "\n",
            du.bred("  The `--purge` option explicitly requires the `--omit-backup` option. Quit."),
            "\n",
        )
        exit()
    else:
        answer = input(f" -> {du.yellow('purging')} <{args.target}>/{target_deployment_path} (y/N)")
        if answer != "y":
            print(du.bred("Aborted."))
            exit()
        c.run(f"rm -r {target_deployment_path}", target_spec="both")


def install_app(c):
    c.activate_venv(f"~/{venv}/bin/activate")

    c.chdir(target_deployment_path)
    c.run(f"pip install -r requirements.txt", target_spec="both")


def initialize_db(c):

    c.chdir(target_deployment_path)

    # try to backup db before (re-)initialization and changing database layout
    # print("\n", "backup old database", "\n")
    _ = c.run("python manage.py savefixtures --backup", warn=False)


    c.run("python manage.py makemigrations", target_spec="both")

    # delete old db
    c.run("rm -f db.sqlite3", target_spec="both")

    # this creates the new database
    c.run("python manage.py migrate", target_spec="both")

    # create superuser with password from config
    c.chdir(target_deployment_path)
    cmd = f'export DJANGO_SUPERUSER_PASSWORD="{config("dep::ADMIN_PASS")}"; '
    cmd += f'python manage.py createsuperuser --noinput --username {config("dep::ADMIN_NAME")} --email "a@b.org"'
    # c.run(cmd)

    # print("\n", "install initial data", "\n")

    # TODO: implement option to load latest backup
    # c.run(f"python manage.py loaddata {init_fixture_path}", target_spec="both")



def generate_static_files(c):

    c.chdir(target_deployment_path)

    # TODO: this does not yet work (and must be run and copied manually)

    c.run("python manage.py collectstatic --no-input", target_spec="remote")

    print("\n", "copy static files to the right place", "\n")
    c.chdir(f"/var/www/virtual/{user}/html")
    c.run(f"rm -rf ./{static_url_prefix}")
    c.run(f"cp -r {static_root_dir} ./{static_url_prefix}")

    c.chdir(target_deployment_path)



if args.debug:
    # create_and_setup_venv(c)
    c.activate_venv(f"{venv_path}/bin/activate")
    render_and_upload_config_files(c)

    # c.deploy_local_package("/home/ck/projekte/rst_python/ipydex/repo")
    # set_web_backend(c)

    IPS()
    exit()

if args.initial:

    create_and_setup_venv(c)
    render_and_upload_config_files(c)
    update_supervisorctl(c)
    set_web_backend(c)

if args.purge:
    purge_deployment_dir(c)

upload_files(c)

if not args.omit_requirements:
    install_app(c)

if not args.omit_database:
    initialize_db(c)

if not args.omit_static:
    generate_static_files(c)


print("\n", "restart uwsgi service", "\n")
c.run("supervisorctl restart all", target_spec="remote")


print(final_msg)
