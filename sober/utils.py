import os
import json
import re
import tempfile
from django.core.management import call_command
from ipydex import IPS


default_deployment_fixture = "for_test_deployment/deployment_data_stripped.json"
default_backup_fixture = "for_test_deployment/backup_all.json"
default_unittest_fixture = "for_unit_tests/all.json"


def get_path(reason):
    assert reason in ["locale", "templates", "static", "fixtures"]
    basepath = os.path.dirname(os.path.abspath(__file__))
    res_path = os.path.join(basepath, reason)

    return res_path


def get_present_db_content():
    """

    Expected to be run from the django project (e.g. sober-site)
    """

    tmpfname = tempfile.mktemp()
    cmd = "python3 manage.py dumpdata > {}".format(tmpfname)
    # cmd = "python3 manage.py dumpdata | jsonlint -f > {}".format(tmpfname)

    save_run_command(cmd)

    with open(tmpfname) as jfile:
        data = json.load(jfile)

    os.remove(tmpfname)

    return data


def strip_fixtures(fname=None, jsonlint=True):
    """
    Loads a json-file or present db-content and strips all entries whose model is on the hardcoded blacklist.
    Leads to a tractable fixture file.
    :return:
    """

    model_blacklist = ["contenttypes*", "sessions*", r"admin\.logentry",
                       r"auth\.permission", ]

    blacklist_re = re.compile("|".join(model_blacklist))
    fixture_path = get_path("fixtures")

    if fname is None:

        data = get_present_db_content()
        opfname = default_backup_fixture.replace(".json", "_stripped.json")
        output_path = os.path.join(fixture_path, opfname)

    else:
        if fname == "__default__":
            fname = default_backup_fixture

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


def load_fixtures_to_db(fname=None):
    """
    This is a helper from the django-app "sober" for setting up the django-project (e.g. "sober_site")
    It executes `python3 manage.py loaddata ...` with the appropriate file (and its path)

    It is supposed to be run in sober_site-dir with the command:

        `python3 -c "import sober.utils as u; u.load_fixtures_to_db()"`

    :param fname:   bare filename (default loads usual sample data)
    :return:        None
    """

    if fname is None:
        fname = default_deployment_fixture

    fixture_path = get_path("fixtures")
    target_path = os.path.join(fixture_path, fname)

    if not os.path.isfile(target_path):
        raise FileNotFoundError("{} not found!".format(fname))

    cmd = "python3 manage.py loaddata {}".format(target_path)
    save_run_command(cmd)


def save_run_command(cmd):
    print("The following command will be executed on your system:\n\n {}".format(cmd))

    res = input("\nDo you want to proceed (y/N)? ")
    if res in ["y", "yes"]:
        rcode = os.system(cmd)
        if rcode != 0:
            print("\nThere were some errors.\n")
        else:
            print("\nDone.\n")
    else:
        print("Abort.")


def main():
    # expected to be run with python3 -c "import sober.utils as u; u.main()"
    # get_present_db_content()
    strip_fixtures()
