# django-sober - worthwhile discussions

Sober is a [django](https://www.djangoproject.com/) app which provides a structured way to visualize discussion.

Currently (December 2018) it is still in early stage of development (alpha-status).

For deployment information see the project: [django-sober-site][1]

[1]: https://github.com/cknoll/django-sober-deployment-project


A demonstration server is available at https://sober-arguments.net


## Background

This web application was developed out of the experience that discussions via email, social media,
comment areas or classical forums in many cases are frustrating. Some observed reasons:

- The lack of reference and unsupported claims
- The lack of focus (vulnerability to so called [red herrings](https://en.wikipedia.org/wiki/Red_herring))
- Important arguments are hidden in volumes of less important text
- The lack of overview (which argument relates to which)

`Sober` was designed to avoid these problems as much as possible, while still being easy to use.
The intended audience are groups of people who in principle are willing to collaborate and making
decisions based on thoroughly weighted arguments.

Main features are
- Discussions are strongly formalized and split up into atomic contributions, so called *bricks*.
- The basis of each discussion is a *thesis*-brick.
- Answers to a thesis must have one of the following types:
    - pro-argument
    - counter-argument
    - improvement suggestion
    - question
    - comment
- The quality of each brick can be rated.
    - Theses can evoke more or less *agreement*.
    - Arguments can have more or less *cogency* (persuasive power).
    - Other bricks can have more or *relevance*.
- Users are enabled and encouraged to gradually improve bricks: find better references, use more clear formulation, etc.
- Authorship of bricks is not shown to emphasize content over social interdependencies.
- `Sober` is [free software](#License) and aims to be easily deployable on self hosted infrastructure.

Main use cases are
- Support running processes of formation of opinion and collective decision making within groups
- Document such processes (which might have taken place on other media or offline) for later reference

## Future development
As stated, the software is currently in alpha-status and might be considered as an experimental proof of concept.
It serves to generate some feedback and ideally some reinforcement of the development team.
Reporting issues is encouraged, filing PRs even more.
Contributing guide is in preparation.


## Alternatives

There are other plattforms and apps which have similar aims.
However, they either seem to complicated or lack some features like the self-hosting-ability

- https://socratrees.azurewebsites.net/
- https://www.kialo.com/
- http://en.arguman.org/
- https://brabbl.com/
