"""
See `simple_page_interface.py` for a description of the simple_page-system.
"""

import collections
from django.utils.translation import gettext as _
from .simple_pages_core import get_project_READMEmd, dupurls, SimplePage


sp_unknown = SimplePage(type="unknown",
                        title="unknown",
                        content="This page is unknown. Please go back to `home`.")

splist = [sp_unknown]


# Defining this function here in the content file results in some code-duplication but is the easiest approach.
def new_sp(**kwargs):
    sp = SimplePage(**kwargs)
    splist.append(sp)
    return sp


# ----------------------------------------------------------------------------
settings = True  # the purpose of these boolean variables is currently unclear (2019-09-07 22:43:27)

new_sp(type="settings",
       title="Settings",
       content="In the future you can configure some settings here.")

# ----------------------------------------------------------------------------
internationla__inzn_test = True

new_sp(type="__inzn_test",
       title="international_english",
       content="international_test_text_englisch_(original)",
       utc_comment="utc_international_test_text_en")

new_sp(type="__inzn_test__de",
       title="international_deutsch",
       content="international_test_deutsch",
       utc_comment="utc_international_test_text_de")

new_sp(type="__inzn_test__es",
       title="international_español",
       content="international_test_español",
       utc_comment="utc_international_test_text_es")

# ----------------------------------------------------------------------------

# !! hcl (TODO: translate error message)
new_sp(type="voting_not_allowed_login",
       title=_("Voting not allowed"),
       content=_("Voting is only allowed for logged in users."),
       utc_comment="utc_voting_not_allowed_login")

# ----------------------------------------------------------------------------
imprint = True


new_sp(type="imprint",
       title="Legal Notice",
       utc_comment="utc_imprint_en",
       content="""
## Legal Notice


This website is maintained by Carsten Knoll.
This website contains external links.
We can not assume any liability for the content of such external websites because they are not under our control.
This website contains content which was created and/or edited by users which are unknown to the maintainer.
We strive for compliance with all applicable laws and try to remove unlawful or otherwise inappropriate content.
However we can not guarantee the immediate removal.
Should there be any problem with the operation or the content of this website, please contanct the maintainer.
<br><br>
Contact information: \n\n
- <http://cknoll.github.io/pages/impressum.html>\n
- <https://github.com/cknoll/django-sober>
""")


new_sp(type="imprint__de",
       title="Impressum",
       utc_comment="utc_imprint_de",
       content="""
## Impressum

Diese Seite wird betrieben von Carsten Knoll.
Haftung für Links auf externe Seiten wird explizit nicht übernommen.
Diese Seite enthält Inhalte die von dem Betreiber unbekannten Benutzern eingestellt werden.
Der Betreiber bemüht sich, eventuelle Ordnungs- oder Gesetzeswidrigkeiten schnellstmöglich zu entfernen,
kann aber nicht dafür garantieren.
Sollte es ein Problem mit dem Betrieb oder den Inhalten der Seite geben, kontaktieren Sie bitte den Betreiber.
<br><br>
Kontaktinformationen: \n\n
- <http://cknoll.github.io/pages/impressum.html>\n
- <https://github.com/cknoll/django-sober>
""")


# ----------------------------------------------------------------------------
contact = True

new_sp(type="contact",
       title="Contact",
       utc_comment="utc_contact_en",
       content="""
This site is maintained by Carsten Knoll. For contact information see: \n\n
- <http://cknoll.github.io/pages/impressum.html>\n
- <https://github.com/cknoll/django-sober>
"""
       )

new_sp(type="contact__de",
       title="Kontakt",
       utc_comment="utc_contact_de",
       content="""
Diese Seite wird betrieben von Carsten Knoll.
Weitere Kontaktinformationen: \n\n
- <http://cknoll.github.io/pages/impressum.html>\n
- <https://github.com/cknoll/django-sober>
"""
)


# ----------------------------------------------------------------------------
privacy = True

new_sp(type="privacy",
       title=_("Privacy rules"),
       utc_comment="utc_privacy_en",
       content="""
## Privacy rules

This website aims for data **frugality**.
We only collect data which is necessary to operate this website or which is explicitly
submitted voluntarily by the user.
We use **cookies** to enable an interal area which serves to store settings and manage
access-rights for content.

In particular we collect and process the following data:

 - Content (if voluntarily submitted)
 - Email-address (if voluntarily submitted; neccessary to communicate with users)
 - Webserverlogs (contains ip-addresses, browser version and url of origin("referer");
 Duration of storage of this data: 14 day; This data is collected to prevent abuse and facilitate secure operation
 of this website; See also  [Reason 49](https://dsgvo-gesetz.de/erwaegungsgruende/nr-49/))

If you have questions or requests (e.g. Correction or Deletion of data ) please contact the maintainer of this website,
see [contact]({}).
""".format(dupurls["contact-page"])
       )


new_sp(type="privacy__de",
       title=_("Datenschutzrichtlinie"),
       utc_comment="utc_privacy_de",
       content="""
## Datenschutzrichtlinie

Diese Seite orientiert sich am Prinzip der **Datensparsamkeit**
und erhebt nur Daten, die für den Betrieb des Dienstes notwendig sind und
im Wesentlichen freiwillig übermittelt werden.
Die Seite setzt **Cookies** ein, um einen internen
Bereich zu ermöglichen, der zur Speicherung von Einstellungen und
dem Management von Zugriffsberechtigungen auf Inhalte dient.

Im Einzelen werden folgende Daten erfasst und verarbeitet.:

 - Inhalte (wenn freiwillig angegeben, offensichtlich notwendig für den Betrieb der Seite)
 - E-Mail-Adresse (wenn freiwillig angegeben, notwendig zur Kommunikation mit Nutzer:innen)
 - Webserverlogs (beinhalten IP-Adressen, Browser-Version und Herkunftsseite ("Referer");
 Speicherdauer 14 Tage; Notwendig zum Schutz gegen Missbrauch und zum sicheren Betrieb der Webseite;
 [Erwägungsgrund 49](https://dsgvo-gesetz.de/erwaegungsgruende/nr-49/))

Bei Fragen bzw. Anfragen (z.B. Richtigstellung und Löschung von Daten) wenden Sie sich bitte den Betreiber der Seite.
Siehe [Kontakt]({}).

""".format(dupurls["contact-page"])
       )

# ----------------------------------------------------------------------------
welcome = True

# Welcome-text:
welcome_txt1 = """
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

welcome_txt2 = """
[Read more](/about)

<hr class="hr_style_gradient">
Below you see a list of publicly visible theses:
"""

tmp1 = get_project_READMEmd("<!-- marker_1 -->", "<!-- marker_2 -->")
tmp3 = get_project_READMEmd("<!-- marker_3 -->", "<!-- marker_4 -->")

welcome_txt3 = "{} (see Details above) {}".format(tmp1, tmp3)


usage_txt = """
<hr class="hr_style_gradient">

## Getting started

You have to be logged in to fully use this webservice.
Then you can

- create a Thesis,
- create Bricks (Pro/Contra-Arguments, Improvement Suggestions, etc.),
- edit your Bricks and
- vote on Bricks.

If you want to try it out: [register]({}) or [login]({}) now.
Alternatively, got to [thesis list]({}).
""".format(dupurls["register_page"], dupurls["login_page"], dupurls["thesis_list"])

txt1 = "{}\n{}\n{}".format(welcome_txt1, welcome_txt3, usage_txt)

new_sp(type="about",
       title="About Sober",
       content=_(txt1))

txt2 = "{}\n{}".format(welcome_txt1, welcome_txt2)


# the following sp-object is never rendered directly but evaluated by a view
new_sp(type="landing_page",
       title="sober discussion landing page",
       content=_(txt2))

# ----------------------------------------------------------------------------


# create a defaultdict of all simple pages with sp.type as key
items = ((sp.type, sp) for sp in splist)
# noinspection PyArgumentList
sp_defdict = collections.defaultdict(lambda: sp_unknown, items)
