import collections
from django.utils.translation import gettext as _

SimplePage = collections.namedtuple("SimplePage", "type title content")

sp_unknown = SimplePage(type="unknown",
                        title="unknown",
                        content="This page is unknown. Please go back to `home`.")

splist = [sp_unknown]


def new_sp(**kwargs):
    splist.append(SimplePage(**kwargs))

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

utc_comment = "\n<-- utc_voting_not_allowed_login -->"
new_sp(type="voting_not_allowed_login",
       title=_("Voting not allowed"),
       content=_("Voting is only allowed for logged in users.") + utc_comment)

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
       title="Datenschutz",
       content=txt)

# create a defaultdict of all simple pages with sp.type as key
items = ((sp.type, sp) for sp in splist)
# noinspection PyArgumentList
defdict = collections.defaultdict(lambda: sp_unknown, items)
