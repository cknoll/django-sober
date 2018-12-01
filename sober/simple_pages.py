import collections
from django.utils.translation import gettext as _


class SimplePage(object):
    def __init__(self, type, title, content, utc_comment=""):
        self.type = type
        self.title = title
        self.content = content
        self.utc_comment = utc_comment


sp_unknown = SimplePage(type="unknown",
                        title="unknown",
                        content="This page is unknown. Please go back to `home`.")

splist = [sp_unknown]


def new_sp(**kwargs):
    sp = SimplePage(**kwargs)
    splist.append(sp)
    return sp

new_sp(type="about",
       title="About",
       content="In the future you will read an about text here.")

new_sp(type="settings",
       title="Settings",
       content="In the future you can configure some settings here.")

# !!hcl
new_sp(type="impressum",
       title="Impressum",
       content="Diese Seite wurde erstellt von Carsten Knoll. "
               "Weitere Kontaktinformationen: "
               "http://cknoll.github.io/pages/impressum.html")

# !!hcl
new_sp(type="kontakt",
       title="Kontakt",
       content="Diese Seite wurde erstellt von Carsten Knoll. "
               "Weitere Kontaktinformationen: "
               "http://cknoll.github.io/pages/impressum.html")

new_sp(type="international",
       title="international", content=_("international_test_text"))

new_sp(type="voting_not_allowed_login",
       title=_("Voting not allowed"),
       content=_("Voting is only allowed for logged in users."),
       utc_comment="utc_voting_not_allowed_login")

txt = \
    """
    Diese Seite orientiert sich am Prinzip der Datensparsamkeit "
    und erhebt nur Daten, die für den Betrieb des Dienstes notwendig sind und
    freiwillig übermittelt werden. Die Seite setzt Cookies ein, um einen internen
    Bereich zu ermöglichen. Dieser dient zur Speicherung von Einstellungen und
    dem Rechte-Management (Wer darf welche Texte lesen und editieren).
    """

# !! hcl
new_sp(type="datenschutz",
       title=_("Datenschutz"),
       content=_(txt))

# Welcome-text:
txt = \
"""
## Welcome...
... to sober-discussion.net. This web applications aims to enable
constructive discussion. Each discussion consists of so called *bricks*.
The basic brick for every discussion is a *Thesis-Brick*.
For each thesis one can state *Pro*- or *Contra-Arguments*, *Improvement Suggestions*,
*Questions* or unspecified *Comments*. Each of theses bricks can have child bricks as well.
Every brick can be *rated* such that over time it gets obvious which are the most important
arguments, which need to be formulated better or backed up with better sources
and which arguments contain flaws or are simply not convincing.


To keep emotions out of discussions, the authorship of bricks is not displayed.
"""

new_sp(type="landing_page",
       title="sober discussion landing page",
       content=_(txt))


# create a defaultdict of all simple pages with sp.type as key
items = ((sp.type, sp) for sp in splist)
# noinspection PyArgumentList
defdict = collections.defaultdict(lambda: sp_unknown, items)

