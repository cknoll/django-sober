from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import collections

from .models import Brick
from .simple_pages import defdict as sp_defdict

from ipydex import IPS

brick_ordering = ['type', 'cached_avg_vote', 'update_datetime']
brick_ordering_chrono = ['type', 'creation_datetime']

template_mapping = {Brick.thesis: "brick_thesis.html",
                    Brick.pro: "brick_pro.html",
                    Brick.contra: "brick_contra.html",
                    Brick.question: "brick_question.html",
                    Brick.comment: "brick_comment.html",
                    }

symbol_mapping = {Brick.thesis: "!",
                  Brick.pro: "✓",
                  Brick.contra: "⚡",
                  Brick.question: "?",
                  Brick.comment: '"',
                 }

# the following solves the problem that adhoc attributes attached to Model instances are not saved in the database
# if the same instance is restrieved later again (e.g. in recursive function calls) the attribute is lost.
# we store it in a dict {(pk, attrname): value}
brick_attr_store = {}


# empty object to store some attributes at runtime
class Container(object):
    pass


def index(request):

    # get a list of all thesis-bricks

    thesis_list = Brick.objects.filter(type=Brick.thesis)

    root_object = Container()
    root_object.title = "List of Theses"

    for tbrick in thesis_list:
        tbrick.template = "sober/{}".format(template_mapping.get(tbrick.type))
    root_object.sorted_child_list = thesis_list

    return render(request, 'sober/main_brick_tree.html', {'root': root_object})
    # return render(request, 'sober/main_simple_page.html', {})


def simple_page(request, pagetype=None):
    """
    Render (almost) static page
    :param request:
    :param pagetype:
    :return:
    """

    context = {"pagetype": pagetype, "sp": sp_defdict[pagetype]}
    return render(request, 'sober/main_simple_page.html', context)


def renderbrick_l0(request, brick_id=None):
    """
    Top level rendering of a brick

    :param request:
    :param brick_id:
    :return:
    """
    base_brick = get_object_or_404(Brick, pk=brick_id)

    base_brick.sorted_child_list = process_child_bricks(base_brick,
                                                        root_type=base_brick.type,
                                                        current_level=0, max_level=20)

    # let the base know how many childs of each type it has
    base_brick.child_type_counter = brick_attr_store[(base_brick.pk, "child_type_counter")]
    set_child_type_counters(base_brick)

    return render(request, 'sober/main_brick_tree.html', {'root': base_brick})


# ------------------------------------------------------------------------
# below are auxiliary functions which do not directly produce a view
# ------------------------------------------------------------------------


def process_child_bricks(brick, root_type, current_level, max_level):
    """
    This function will be called recursively.
    It sets the
     - level
     - template
     - title_tag (string)
     of the brick, and looks for childs and processes them.

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

    type_counter = collections.Counter()
    # iterate over all children to fix their chronological order (see the use of typed_idx below)
    for b in brick.children.all().order_by(*brick_ordering_chrono):
        type_counter.update([b.type])
        # e.g. dertermine that this is the 3rd pro-brick on the current level
        brick_attr_store[(b.pk, "typed_idx")] = type_counter[b.type]

    # save the whole counter in the store.
    # this enables us to display how much pro and contra args there are
    brick_attr_store[(brick.pk, "child_type_counter")] = type_counter

    # Indentation (margin-left (ml)) should depend on the current (pseudo-)root
    # this logic could be implemented in the templates but would look ugly there (due to the lack of real variables)
    if root_type == brick.thesis:
        brick.indentation_class = "ml{}".format(max([0, current_level - 1]))
    else:
        brick.indentation_class = "ml{}".format(current_level)

    # now set the template

    brick.template = "sober/{}".format(template_mapping.get(brick.type))

    # now determine the title tag (something like pro#3⚡2⚡1?3)

    # if brick was the root
    if brick_attr_store.get((brick.pk, "typed_idx")) is None:
        brick_attr_store[(brick.pk, "typed_idx")] = 1

    if brick.parent is None or \
            brick.parent.type not in [Brick.pro, Brick.contra]:  # arguments following a Thesis start with new count
        # hcl!!
        type_str = Brick.types_map[brick.type]
        if brick.type == Brick.thesis:
            brick.title_tag = "{}##{}".format(type_str, brick.pk)
        else:
            typed_idx = brick_attr_store[(brick.pk, "typed_idx")]
            brick.title_tag = "{}#{}".format(type_str, typed_idx)
    else:
        split_symbol = symbol_mapping[brick.type]
        typed_idx = brick_attr_store[(brick.pk, "typed_idx")]
        brick.title_tag = "{}{}{}".format(brick.parent.title_tag, split_symbol, typed_idx)

    # now apply this function recursively to all child-bricks
    res = [brick]
    direct_children = brick.children.all().order_by(*brick_ordering)

    for i, b in enumerate(direct_children):
        res.extend(process_child_bricks(b, root_type, current_level + 1, max_level))

    return res


def set_child_type_counters(brick):
    """
    create attributes like brick.child_type_counter_pro (how many pro-childs does this brick have?)

    :param brick:   Brick
    :return:        None
    """

    for key, type_str in Brick.types:
        # get the counter (dict-like object) from the store and evaluate it with the type `key`

        ctc = brick_attr_store[(brick.pk, "child_type_counter")].get(key, 0)

        attr_name = "number_of_childs_{}".format(type_str.lower())
        setattr(brick, attr_name, ctc)
        print("set_ctc:", brick, key, ctc,)
