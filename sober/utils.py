import os
import json
import re
import tempfile
import time
from django.core.management import call_command
from ipydex import IPS


default_deployment_fixture = "for_test_deployment/deployment_data_stripped.json"
default_backup_fixture = "for_test_deployment/backup_all.json"
default_unittest_fixture = "for_unit_tests/all.json"


def get_path(reason):
    assert reason in ["locale", "templates", "static", "fixtures", "migrations"]
    basepath = os.path.dirname(os.path.abspath(__file__))
    res_path = os.path.join(basepath, reason)

    return res_path


# noinspection PyPep8Naming
def get_project_READMEmd(marker_a=None, marker_b=None):
    """
    Return the content of README.md from the root directory of this project

    (optionally return only the text between the two marker-strings)
    :return:
    """

    basepath = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(basepath)
    fpath = os.path.join(project_root, "README.md")
    with open(fpath, "r") as txt_file:
        txt = txt_file.read()

    if marker_a is None:
        assert marker_b is None
        return txt
    else:
        assert marker_b is not None

    idx1 = txt.index(marker_a) + len(marker_a)
    idx2 = txt.index(marker_b)

    return txt[idx1:idx2]






def get_present_db_content():
    """

    Expected to be run from the django project (e.g. sober-site)
    """

    tmpfname = tempfile.mktemp()
    cmd = "python3 manage.py dumpdata > {}".format(tmpfname)
    # cmd = "python3 manage.py dumpdata | jsonlint -f > {}".format(tmpfname)

    safe_run_command(cmd)

    with open(tmpfname) as jfile:
        data = json.load(jfile)

    os.remove(tmpfname)

    return data


def save_stripped_fixtures(fname=None, jsonlint=True):
    """
    Loads a json-file or present db-content and strips all entries whose model is on the hardcoded blacklist.
    Leads to a tractable fixture file.

    Expected to be run with

        python3 -c "import sober.utils as u; u.save_stripped_fixtures()"

    :return: None
    """

    model_blacklist = ["contenttypes*", "sessions*", r"admin\.logentry",
                       r"auth\.permission", r"captcha\.captchastore"]

    blacklist_re = re.compile("|".join(model_blacklist))
    fixture_path = get_path("fixtures")

    if fname is None:

        data = get_present_db_content()
        opfname = default_deployment_fixture
        output_path = os.path.join(fixture_path, opfname)

    else:
        # assume that the file exists; else `open(...)` will fail

        input_path = os.path.join(fixture_path, fname)
        fname2 = fname.replace(".json", "_stripped.json")
        output_path = os.path.join(fixture_path, fname2)

        with open(input_path) as jfile:
            data = json.load(jfile)

    keep_data = []
    bad_data = []
    for d in data:
        model = d.get("model")
        if model is None:
            continue
        if blacklist_re.match(model):
            # just for debugging
            bad_data.append(model)
            continue
        else:
            keep_data.append(d)

    # dependency only needed here
    import demjson
    res = demjson.encode(keep_data, encoding="utf-8", compactly=False)

    # write bytes because we have specified utf8-encoding
    with open(output_path, "wb") as jfile:
        jfile.write(res)

    print("file written:", output_path)


def load_fixtures_to_db(fname=None, ask=True):
    """
    This is a helper from the django-app "sober" for setting up the django-project (e.g. "sober_site")
    It executes `python3 manage.py loaddata ...` with the appropriate file (and its path)

    It is supposed to be run in sober_site-dir with the command:

        `python3 -c "import sober.utils as u; u.load_fixtures_to_db()"`

    :param fname:   bare filename (default loads usual sample data)
    :param ask:     Boolean flag whether to ask befor executing the command
    :return:        None
    """

    if fname is None:
        fname = default_deployment_fixture

    fixture_path = get_path("fixtures")
    target_path = os.path.join(fixture_path, fname)

    if not os.path.isfile(target_path):
        raise FileNotFoundError("{} not found!".format(fname))

    cmd = "python3 manage.py loaddata {}".format(target_path)
    safe_run_command(cmd, ask)


def safe_run_command(cmd, ask=True):
    """
    :param cmd:     The command to execute
    :param ask:     Boolean flag whether to ask befor executing the command
    :return:
    """
    print("The following command will be executed on your system:\n\n {}".format(cmd))

    if ask:
        res = input("\nDo you want to proceed (y/N)? ")
    else:
        res = "y"
    if res in ["y", "yes"]:
        rcode = os.system(cmd)
        if rcode != 0:
            print("\nThere were some errors.\n")
        else:
            print("\nDone.\n")
    else:
        print("Abort.")


def restart_with_clean_db(ask=True):

    """
    - Move the current db-file (assuming sqlite) to a backup-place.
    - Delete all migrations
    - Install default deployment fixtures

    expected to be run inside the sober site dir

        python3 -c "import sober.utils as u; u.restart_with_clean_db()"

    :param ask:     Boolean flag whether to ask befor executing the command

    :return: None
    """

    tstr = time.strftime(r"%Y-%m-%d--%H-%M-%S")

    dbfname = "db.sqlite3"
    cmd1 = "mv -v {0} {0}_{1}".format(dbfname, tstr)
    safe_run_command(cmd1, ask)

    # delete migrations
    mpath = get_path("migrations")
    cmd2 = "rm -v {}/0*.py".format(mpath)
    safe_run_command(cmd2, ask)

    safe_run_command("python3 manage.py makemigrations", ask)
    safe_run_command("python3 manage.py migrate", ask)

    load_fixtures_to_db(default_deployment_fixture, ask)


def ensure_data_integrity():
    """
    # this function is useful after manual interaction with the data

    all thesis-objects must have parent=None
    all child-bricks mus have the same group settings as the root_parent
    all users should be at least in the public group

    :return:
    """
    from sober.models import Brick, User, AuthGroup
    # iterate over all thesis
    for b in Brick.objects.filter(type=1):
        assert b.parent is None

    # ensure that child bricks have the same group setting
    for b in Brick.objects.all():
        rp = b.get_root_parent()[0]

        if False:
            # temporarily mitigate invalid fixtures
            b.associated_group = rp.associated_group
            b.allowed_for_additional_groups.set(rp.allowed_for_additional_groups.all())
            b.save()

        assert b.associated_group == rp.associated_group
        l1 = list(b.allowed_for_additional_groups.all())
        l2 = list(rp.allowed_for_additional_groups.all())

        if not l1 == l2:
            # IPS()
            msg = "Invalid groups for Brick {}".format(b)
            raise ValueError(msg)

        assert l1 == l2, "test"

    # find groups with pk 1, 2, 3, 4
    special_groups = AuthGroup.objects.filter(pk__lte=4)
    special_groups.order_by("pk")
    assert len(special_groups) == 4

    assert special_groups[0].name == "public"
    assert special_groups[1].name == "public__ro"
    assert special_groups[2].name == "registered_users"
    assert special_groups[3].name == "registered_users__ro"

    pub_group = AuthGroup.objects.filter(pk=1)[0]

    for u in User.objects.all():
        groups = u.groups.all()
        msg = "Problematic user: {}".format(u)
        assert pub_group in groups, msg

    return True


def main():
    # expected to be run with python3 -c "import sober.utils as u; u.main()"
    # get_present_db_content()
    # strip_fixtures()
    pass
