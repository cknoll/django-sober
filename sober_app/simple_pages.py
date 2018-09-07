import collections
from django.utils.translation import gettext as _

SimplePage = collections.namedtuple("SimplePage", "title content")

sp_unknown = SimplePage(title="unknown",
                        content="This page is unknown. Please go back to `home`.")

splist = [sp_unknown]


def new_sp(**kwargs):
    splist.append(SimplePage(**kwargs))

new_sp(title="About",
       content="In the future you will read an about text here.")

new_sp(title="Settings",
       content="In the future you can configure some settings here.")

new_sp(title="Impressum",
       content="Diese Seite wurde erstellt von Carsten Knoll. "
               "Weitere Kontaktinformationen: "
               "http://cknoll.github.io/pages/impressum.html")

new_sp(title="Kontakt",
       content="Diese Seite wurde erstellt von Carsten Knoll. "
               "Weitere Kontaktinformationen: "
               "http://cknoll.github.io/pages/impressum.html")

new_sp(title="international", content=_("international_test_text"))

txt = \
"""
Diese Seite orientiert sich am Prinzip der Datensparsamkeit "
und erhebt nur Daten, die für den Betrieb des Dienstes notwendig sind und
freiwillig übermittelt werden. Die Seite setzt Cookies ein, um einen internen
Bereich zu ermöglichen. Dieser dient zur Speicherung von Einstellungen und
dem Rechte-Management (Wer darf welche Texte lesen und editieren).
"""
new_sp(title="Datenschutz",
       content=txt)

# create a defdict of all simple pages (assume title.lower()=pagetype)
items = ((sp.title.lower(), sp) for sp in splist)
# noinspection PyArgumentList
defdict = collections.defaultdict(lambda: sp_unknown, items)
