[![CircleCI](https://circleci.com/gh/cknoll/django-sober/tree/main.svg?style=shield)](https://circleci.com/gh/cknoll/django-sober/tree/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# django-sober - worthwhile discussions

Sober is a [django](https://www.djangoproject.com/) app which provides a structured way to visualize discussion.

Currently (Jan. 2019) it is still in early stage of development (alpha-status).
The motivation of this app was summarized in a Lightning Talk at 35C3
([video](https://media.ccc.de/v/35c3-9568-lightning_talks_day_4#t=198),
[slides](https://github.com/cknoll/django-sober/raw/public_relations/pr/2018-sober-35c3-slides.pdf)).

A demonstration server is available at https://sober-arguments.net

For deployment information see the project: [django-sober-site][1]

[1]: https://github.com/cknoll/django-sober-deployment-project

## Background
<!-- Note: this file contains some comment-markers which enable the reusage of the text-content at sober-arguments.net/about  -->
<!-- marker_1 -->
*Sober* was developed out of the experience that discussions via email, social media, comment areas or classical forums in many cases are frustrating. Some observed reasons:

- The lack of reference and unsupported claims.
- The lack of focus (vulnerability to so called [red herrings](https://en.wikipedia.org/wiki/Red_herring)).
- Important arguments are hidden in volumes of less important text.
- The lack of overview (which argument relates to which).
- Formation or manifestation of rival camps.

*Sober* was designed to avoid these problems as much as possible, while still being easy to use. The intended audience are groups of people who in principle are willing to collaborate and making decisions based on reasonable arguments.
Main features are:

- Discussions are strongly formalized and split up into atomic contributions, so called *bricks*<!-- marker_2 -->.
- The basis of each discussion is a *thesis*-brick.
- Answers to a thesis must have one of the following types:
    - pro-argument
    - counter-argument
    - improvement suggestion
    - question
    - comment<!-- marker_3 -->
- The quality of each brick can be rated.
    - Theses can evoke more or less *agreement*.
    - Arguments can have more or less *cogency* (persuasive power).
    - Other bricks can have more or less *relevance*.
- Users are enabled and encouraged to gradually improve bricks: find better references, use clearer formulation, etc.
- Authorship of bricks is not shown. This is to emphasize content over social interdependencies.
- *Sober* is [free software](https://github.com/cknoll/django-sober#license) and aims to be easily deployable on self hosted infrastructure.

Main use cases are:

- Loose interchange of arguments on a possibly controversial topic.
- Support running processes of formation of opinion and collective decision-making within groups.
- Document such processes (which might have taken place on other media or offline) for later reference.
<!-- marker_4 -->

## Future development
As stated, the software is currently in alpha-status and might be considered as an experimental proof of concept.
It serves to generate some feedback and ideally some reinforcement of the development team.
Reporting issues is encouraged, filing pull requests even more.
A guide for how to contribute is in preparation.

## License
The code of this project is licensed under AGPL.
If you have questions about this, please contact the maintainer.


## Alternatives

There are other platforms and apps which have similar aims.
However, they either seem too complicated or lack some features like the self-hosting-ability

- <https://socratrees.azurewebsites.net/>
- <https://www.kialo.com/>
- <http://en.arguman.org/>
- <https://brabbl.com/>
