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


from django.conf import settings

if True:
    # no setting evaluation yet
    from .simple_pages_content_default import sp_defdict


def get_sp(pagetype, lang=None):

    desired_key = "{}__{}".format(pagetype, lang)

    if desired_key in sp_defdict:
        # return the corrcect language version if possible
        return sp_defdict[desired_key]
    else:
        # return the only available version
        return sp_defdict[pagetype]
