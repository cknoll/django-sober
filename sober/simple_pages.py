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
welcome_txt1 = \
"""
## Welcome...
... to sober-discussion.net. This web applications aims to enable
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

<hr>
Below you see a list of publicly visible theses:

"""

welcome_txt3 = \
"""
A thesis can have many responses (childs) and each of theses bricks
can have many child bricks as well.
Every brick can be *rated* such that over time it gets obvious which are the most important
arguments, which need to be formulated better or backed up with better sources
and which arguments contain flaws or are simply not convincing.

By formally splitting up a discourse into theses, single arguments etc. it is easier
to keep track to both sides of the coin -- and to make valuable contributions.

To keep personal issues out of discussions, the authorship of bricks is not displayed.

### Background
This web application was developed out of the experience that discussions via email,
social media, comment areas or classical forums in many cases are frustrating.
Some observed reasons:

- The lack of references
- The lack of focus (vulnerability to so called
[red herring](https://en.wikipedia.org/wiki/Red_herring))
- Important arguments are hidden in mountains of unimportant text
- The lack of overview (which argument relates to which)

`Sober` was designed to avoid these problems as much as possible,
while still being easy to use. The intended audience are groups of people who
in principle are willing to collaborate and making decisions based on
thoroughly weighted arguments.

`Sober` is [Free Software](https://en.wikipedia.org/wiki/Free_software),
which can be obtained [here](https://todo_add_github_repo).
This instance serves as mainly as demonstration.
If you want to use it in the long run, it would make sense to host you own instance.
"""

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

