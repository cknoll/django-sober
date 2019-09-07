"""
See `simple_page_interface.py` for a description of the simple_page-system.
"""


# noinspection PyUnresolvedReferences
from .utils import get_project_READMEmd, duplicated_urls as dupurls


class SimplePage(object):
    def __init__(self, type, title, content, utc_comment=""):
        self.type = type
        self.title = title
        self.content = content
        self.utc_comment = utc_comment
