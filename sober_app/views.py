from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Brick

from ipydex import IPS

brick_ordering = ['type', 'datetime']  # will be updated soon

template_mapping = {Brick.thesis: "brick_thesis.html",
                    Brick.pro: "brick_pro.html",
                    Brick.contra: "brick_contra.html",
                    Brick.question: "brick_question.html",
                    Brick.comment: "brick_comment.html",
                    }


def index(request):
    return render(request, 'sober/main_index.de.html')


def renderbrick_l0(request, brick_id=None):
    """
    Top level rendering of a brick

    :param request:
    :param brick_id:
    :return:
    """
    base_brick = get_object_or_404(Brick, pk=brick_id)

    # direct_children = base_brick.children.all().order_by(*brick_ordering)

    base_brick.sorted_child_list = process_child_bricks(base_brick, base_brick.type,
                                                        current_level=0, max_level=20)
    # base_brick.sorted_child_list.pop(0)  # first brick is passed separately
    # IPS()

    return render(request, 'sober/main_brick_tree.html', {'brick': base_brick})


# ------------------------------------------------------------------------
# below are auxiliary functions which do not directly produce a view
# ------------------------------------------------------------------------


def process_child_bricks(brick, root_type, current_level, max_level):
    """
    This function will be called recursively.
    Sets the level and the template of the brick, looks for childs and processes them.

    Return a flat list containing this brick and all childs up to max_level.

    :param brick:
    :param root_type:       type of the root brick (used for some css selection)
    :param current_level:
    :param max_level:       int (this is for algorithmic safety.) See notes below

    :return: list of bricks (up to max_level)
    """

    # This max_level is for algorithmic safety only. The display threshold is handled via the template.
    if current_level > max_level:
        return []

    brick.level = current_level

    # Background: indentation (margin-left (ml)) should depend on the current (pseudo-)root
    # this logic could be implemented in the templates but would look ugly there (due to the lack of real variables)
    if root_type == brick.thesis:
        brick.indentation_class = "ml{}".format(max([0, current_level - 1]))
    else:
        brick.indentation_class = "ml{}".format(current_level)

    brick.template = "sober/{}".format(template_mapping.get(brick.type))

    print(brick, brick.template)

    direct_children = brick.children.all().order_by(*brick_ordering)

    res = [brick]

    # noinspection PyPep8
    for b in direct_children:
        res.extend(process_child_bricks(b, root_type, current_level + 1, max_level))

    return res


