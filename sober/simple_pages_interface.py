"""
This module organizes the access to a special kind of content: "simple pages". They consist of markdown text
which is rendered.

While this type of content in principle could live in the database it is much easier to maintain in textfiles.
To support different parallel instances of this app which can have different contents of the simple pages we use the
following structure:

The path to the file `simple_pages_content_custom.py` is configured in the site_specific_config. That file lives
outside of the repo of this app and is provided during deployment (together with the db-content).

If this whole file or a key is not present the content of `simple_pages_content_default.py` is used as fallback.

The logic for this lives in `simple_pages_interface.py`.
The functions and datatypes live in `simple_pages_core.py`

"""

from ipydex import IPS
from collections import defaultdict
from django.conf import settings
from . import utils

# import the simple_page_default_dict for the default content
from .simple_pages_content_default import sp_defdict as sp_defdict_orig

# look if we have custom_content
try:
    SIMPLE_PAGE_CONTENT_CUSTOM_PATH = settings.SIMPLE_PAGE_CONTENT_CUSTOM_PATH
except AttributeError:
    SIMPLE_PAGE_CONTENT_CUSTOM_PATH = None


try:
    simple_pages_content_custom = utils.import_abspath("simple_pages_content_custom", SIMPLE_PAGE_CONTENT_CUSTOM_PATH)
except (FileNotFoundError, ImportError):
    simple_pages_content_custom = None

try:
    sp_defdict_custom = simple_pages_content_custom.sp_defdict
except AttributeError:
    sp_defdict_custom = defaultdict(sp_defdict_orig.default_factory, [])

# now update the default in two steps
# to prevent that keys from first dict are overwritten by the default_factory of 2nd
sp_defdict = defaultdict(sp_defdict_custom.default_factory, sp_defdict_orig.items())
sp_defdict.update(dict(sp_defdict_custom))


def get_sp(pagetype, lang=None):

    desired_key = "{}__{}".format(pagetype, lang)

    if desired_key in sp_defdict:
        # return the corrcect language version if possible
        return sp_defdict[desired_key]
    else:
        # return the only available version
        return sp_defdict[pagetype]
