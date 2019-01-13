import collections
from django.utils.translation import gettext as _
from .utils import get_project_READMEmd


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

new_sp(type="settings",
       title="Settings",
       content="In the future you can configure some settings here.")

# !!hcl
new_sp(type="impressum",
       title="Impressum",
       content="Diese Seite wurde erstellt und wird betrieben von Carsten Knoll. "
               "Haftung für Links auf externe Seiten wird explizit nicht übernommen. "
               "Diese Seite enthält Inhalte die von dem Betreiber unbekannten Benutzern eingestellt werden. Der Betreiber bemüht sich, eventuelle Ordnungs- oder Gesetzeswidrigkeiten schnellstmöglich zu entfernen, kann aber nicht dafür garantieren. "
               "Sollte es ein Problem mit dem Betrieb oder den Inhalten der Seite geben, kontaktieren Sie bitte den Betreiber.<br><br>"
               "Kontaktinformationen: \n\n"
               "- <http://cknoll.github.io/pages/impressum.html>\n"
               "- <https://github.com/cknoll/django-sober>")

# !!hcl (this might be ok here since the url is german)
new_sp(type="kontakt",
       title="Kontakt",
       content="Diese Seite wurde erstellt von Carsten Knoll. "
               "Weitere Kontaktinformationen: \n\n"
               "- <http://cknoll.github.io/pages/impressum.html>\n"
               "- <https://github.com/cknoll/django-sober>")

new_sp(type="contact",
       title="Contact",
       content="This site is maintained by Carsten Knoll. For contact information see: \n\n"
               "- <http://cknoll.github.io/pages/impressum.html>\n"
               "- <https://github.com/cknoll/django-sober>")

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
welcome_txt1 = \
"""
## Welcome...
... to [sober-arguments.net](https://sober-arguments.net).
This web application aims to facilitate
constructive discussions. Each discussion consists of so called *bricks*.
The basic brick for every discussion is a *Thesis-Brick*. A response to a thesis
must have one of the following types:

- Pro-Argument
- Contra-Argument
- Improvement Suggestion
- Question
- Comment

"""

welcome_txt2 = \
"""
[Read more](/about)

<hr class="hr_style_gradient">
Below you see a list of publicly visible theses:
"""

tmp1 = get_project_READMEmd("<!-- marker_1 -->", "<!-- marker_2 -->")
tmp3 = get_project_READMEmd("<!-- marker_3 -->", "<!-- marker_4 -->")

welcome_txt3 = "{} (see Details above) {}".format(tmp1, tmp3)

txt = "{}\n{}".format(welcome_txt1, welcome_txt3)

new_sp(type="about",
       title="About Sober",
       content=_(txt))

txt = "{}\n{}".format(welcome_txt1, welcome_txt2)

new_sp(type="landing_page",
       title="sober discussion landing page",
       content=_(txt))


# create a defaultdict of all simple pages with sp.type as key
items = ((sp.type, sp) for sp in splist)
# noinspection PyArgumentList
defdict = collections.defaultdict(lambda: sp_unknown, items)

