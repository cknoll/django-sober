import collections
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Brick
from .simple_pages import defdict as sp_defdict
from .forms import forms
from .language import lang

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

assert len(symbol_mapping) == len(Brick.type_names_codes)

# the following solves the problem that adhoc attributes attached to Model instances are not saved in the database
# if the same instance is restrieved later again (e.g. in recursive function calls) the attribute is lost.
# we store it in a dict {(pk, attrname): value}
brick_attr_store = {}

# other approach to same problem: save the processed bricks
processed_bricks = {}

# to avoid that this dict grows over time it should be cleared after usage. This could be done by a decorator.


# empty object to store some attributes at runtime
class Container(object):
    pass


def view_index(request):

    # get a list of all thesis-bricks

    thesis_list = Brick.objects.filter(type=Brick.thesis)

    base_object = Container()
    # !! hcl
    base_object.title = "List of Theses"

    base_object.special_head_link = "new_thesis_link"

    for tbrick in thesis_list:
        # trigger processing of the root of the respective trees (sufficient for the index)
        BrickTree(tbrick, max_level=0)

    base_object.sorted_child_list = thesis_list

    return render(request, 'sober/main_brick_tree.html', {'base': base_object})
    # return render(request, 'sober/main_simple_page.html', {})


def view_simple_page(request, pagetype=None):
    """
    Render (almost) static page
    :param request:
    :param pagetype:
    :return:
    """

    context = {"pagetype": pagetype, "sp": sp_defdict[pagetype]}
    return render(request, 'sober/main_simple_page.html', context)


def view_renderbrick(request, brick_id=None):
    """
    Top level rendering of a brick

    :param request:
    :param brick_id:
    :return:
    """
    base_brick = get_object_or_404(Brick, pk=brick_id)

    bt = BrickTree(base_brick)  # process the complete tree

    # use the processed version of base_brick
    base_brick = bt.get_processed_brick(base_brick)
    base_brick.sorted_child_list = bt.get_subtree_as_list(base_brick)

    return render(request, 'sober/main_brick_tree.html', {'base': base_brick})


def view_new_brick(request, brick_id=None, type_code=None):
    """
    create a new brick of a given type (render form)

    :param request:
    :param brick_id:
    :param type_code: one of {th, pa, ca, qu, is}
    :return:
    """

    if type_code not in Brick.typecode_map.keys():
        raise ValueError("Invalid type_code `{}` for Brick".format(type_code))

    sp = Container()
    sp.title = "New {1}-Brick to {0}".format(brick_id, type_code)

    lc = "en"
    sp.long_brick_type = lang[lc]['long_brick_type'][type_code]

    if type_code == Brick.reverse_typecode_map[Brick.thesis]:
        # ensure that we come from the correct url-dispatcher
        assert brick_id == -1
        sp.parent_brick = None

    else:
        sp.parent_brick = prepare_single_brick(brick_id)

    # here we process the submitted form
    if request.method == 'POST':
        brickform = forms.BrickForm(request.POST)

        if not brickform.is_valid():
            # render some error message here
            sp.content = "Errors: {}<br>{}".format(brickform.errors, brickform.non_form_errors)

        else:
            new_brick = brickform.save(commit=False)
            new_brick.parent = sp.parent_brick
            new_brick.type = Brick.typecode_map[type_code]
            new_brick.save()
            sp.newly_fabricated_brick = prepare_single_brick(new_brick.pk, add_level=1)
            sp.content = "no errors. Form saved. Result: {}".format(new_brick)

    # here we handle the generation of an empty form
    else:
        brickform = forms.BrickForm()
        sp.content = ""
        sp.form = brickform

    if hasattr(sp, "form"):
        # sp.form.form_type = "new"

        if type_code == Brick.reverse_typecode_map[Brick.thesis]:
            sp.form.action_url_name = "new_thesis"
        else:
            sp.form.action_url_name = "new_brick"

    context = {"pagetype": "FORM-Mockup", "sp": sp, "brick_id": brick_id, "type_code": type_code}
    return render(request, 'sober/main_simple_page.html', context)


def view_edit_brick(request, brick_id=None):
    sp = Container()

    sp.brick_to_edit = prepare_single_brick(brick_id)

    lc = "en"
    type_code = Brick.reverse_typecode_map[sp.brick_to_edit.type]
    sp.long_brick_type = lang[lc]['long_brick_type'][type_code]
    sp.title = "Edit {1}-Brick with {0}".format(brick_id, sp.long_brick_type)

    # here we process the submitted form
    if request.method == 'POST':
        brickform = forms.BrickForm(request.POST, instance=sp.brick_to_edit)

        if not brickform.is_valid():
            # render some error message here
            sp.content = "Errors: {}<br>{}".format(brickform.errors, brickform.non_form_errors)

        else:
            edited_brick = brickform.save(commit=False)
            edited_brick.update_datetime = timezone.now()
            edited_brick.save()
            sp.newly_fabricated_brick = prepare_single_brick(edited_brick.pk, add_level=1)
            sp.content = "no errors. Form saved. Result: {}".format(edited_brick)

    # here we handle the generation of an empty form
    else:
        brickform = forms.BrickForm(instance=sp.brick_to_edit)
        sp.content = ""
        sp.form = brickform

    if hasattr(sp, "form"):
        # sp.form.form_type = "edit"
        sp.form.action_url_name = "edit_brick"

    context = {"pagetype": "FORM-Mockup", "sp": sp, "brick_id": brick_id, "type_code": None}
    return render(request, 'sober/main_simple_page.html', context)

    pass

# ------------------------------------------------------------------------
# below are auxiliary functions which do not directly produce a view
# ------------------------------------------------------------------------


class BrickTree(object):
    """
    class representing a complete discussion
    """

    def __init__(self, entry_brick, max_level=float("inf")):

        self.root_parent, rp_level = get_root_parent(entry_brick)
        self.processed_bricks = collections.OrderedDict()
        self._process_all_childs(self.root_parent, 0, max_level)

    def _process_all_childs(self, brick, level, max_level=float("inf")):
        """
        for every node set the following attributes:
         - absolute_level
         - template
         - title_tag
         - parent_type_list

        :return:   None
        """

        if level > max_level:
            return

        # if we already processed the brick then we take the respective object from our
        # local store and not from database

        brick = self.processed_bricks.get(brick.pk, brick)
        self.processed_bricks[brick.pk] = brick

        brick.absolute_level = level

        type_counter = collections.Counter()
        # iterate over all children to fix their chronological order (see use of typed_idx below)
        for b in brick.children.all().order_by(*brick_ordering_chrono):
            type_counter.update([b.type])

            # dertermine that this child is e.g. the 3rd pro-brick on the current level
            self.processed_bricks[b.pk] = b
            b.typed_idx = type_counter[b.type]

        # save the whole counter
        brick.child_type_counter = type_counter

        # allow simple access from the template:
        for _, name, _ in Brick.type_names_codes:
            name = name.lower()
            key = getattr(Brick, name)

            setattr(brick, "nbr_" + name, brick.child_type_counter[key])

        brick.template = "sober/{}".format(template_mapping.get(brick.type))

        self._set_title_tag(brick)

        # now apply this method recursively to all child-bricks
        # we save the query as attribute to avoid recomputation later
        brick.direct_children = brick.children.all().order_by(*brick_ordering)

        for i, b in enumerate(brick.direct_children):
            self._process_all_childs(brick=b, level=level + 1, max_level=max_level)

    def _set_title_tag(self, brick):
        """
        determine the title tag (something like pro#3⚡2⚡1?3) and the parent_type_list

        :param brick:
        :return: None (changes brick object)
        """

        if brick.parent is None:
            assert brick.type == Brick.thesis
            # other types must have a parent (!! what is with question?)

            brick.parent_type_list = [(Brick.types_map[brick.type] + "#", brick.pk, brick.pk)]
            # this is a list which stores tuples (split_symbol, xxx, pk) for each parent
            # xxx is pk for thesis and typed_idx for other brick_types

        else:
            assert hasattr(brick.parent, "title_tag")
            assert hasattr(brick.parent, "parent_type_list")
            if not hasattr(brick, "typed_idx"):
                IPS()
            assert hasattr(brick, "typed_idx")

            new_tuple = ( symbol_mapping[brick.type], brick.typed_idx, brick.pk )

            brick.parent_type_list = brick.parent.parent_type_list + [new_tuple]

        brick.title_tag = create_title_tag(brick.parent_type_list)

    def get_subtree_as_list(self, base_brick, max_depth=float("inf")):
        """
        return a render-ready list of bricks

        :param base_brick:
        :param max_depth:           default: inf; 0 -> only the base_brick
        :return:
        """

        assert base_brick is self.processed_bricks[base_brick.pk]
        bricks_to_return = [base_brick]

        subtree_level = 0
        bases = [base_brick]

        while subtree_level < max_depth:
            next_bases = []
            for base in bases:
                # base comes from the database (direct_children is a QuerySet)
                # replace it with the already processed object
                base = self.processed_bricks.get(base.pk)
                if base:
                    next_bases.extend(base.direct_children)
                    bricks_to_return.extend(base.direct_children)

            subtree_level += 1
            if next_bases:
                bases = next_bases
            else:
                break

        final_bricks = []
        for brick in bricks_to_return:
            brick = self.processed_bricks[brick.pk]

            brick.relative_level = brick.absolute_level - base_brick.absolute_level
            if base_brick.type == Brick.thesis:
                brick.indentation_class = "ml{}".format(max([0, brick.relative_level - 1]))
            else:
                brick.indentation_class = "ml{}".format(brick.relative_level)

            final_bricks.append(brick)

        return final_bricks

    def get_processed_brick(self, brick):
        return self.processed_bricks[brick.pk]



def prepare_single_brick(brick_id, add_level=0):

    base_brick = get_object_or_404(Brick, pk=brick_id)
    root_parent, rp_level = get_root_parent(base_brick)

    # use this call to process all bricks down to the sibling level of base_brick
    # set template and relative links etc
    print("pcb", brick_id, "add_level", add_level, "rpl", rp_level)
    process_child_bricks(root_parent,
                         root_type=root_parent.type,
                         current_level=0,
                         rp_level=0,
                         max_level=rp_level,
                         indentation_offset=rp_level-add_level)

    print("--")

    return processed_bricks[base_brick.pk]


def process_child_bricks(brick, root_type, rp_level, current_level, max_level,
                         indentation_offset=0):
    """
    This function will be called recursively.
    It sets the
     - absolute_level (w.r.t. the root_parent)
     - relative_level (w.r.t. the base_brick)
     - template
     - title_tag (string)
     of the brick, and looks for childs and processes them.

    Return a flat list containing this brick and all childs up to max_level.

    :param brick:
    :param root_type:           type of the root brick (used for some css selection)
    :param current_level:       level w.r.t. the tree of the processed brick
    :param rp_level:            level distance between root_parent and shown base_brick
    :param max_level:           int (this is for algorithmic safety.) See notes below
    :param indentation_offset:  int (offset for the indentation-class)

    :return: list of bricks (up to max_level)
    """

    # This max_level is for algorithmic safety only. The display threshold is handled via the template.
    if current_level > max_level:
        return []

    brick.relative_level = current_level
    brick.absolute_level = current_level + rp_level
    brick.indentation_offset = indentation_offset

    type_counter = collections.Counter()
    # iterate over all children to fix their chronological order (see the use of typed_idx below)
    for b in brick.children.all().order_by(*brick_ordering_chrono):
        type_counter.update([b.type])
        # e.g. dertermine that this is the 3rd pro-brick on the current level
        brick_attr_store[(b.pk, "typed_idx")] = type_counter[b.type]

    # save the whole counter in the store.
    # this enables us to display how much pro and contra args there are
    brick_attr_store[(brick.pk, "child_type_counter")] = type_counter

    # Indentation (margin-left (ml)) should depend on the current base_brick
    # this logic could be implemented in the templates
    # but it would look ugly there (due to the lack of real variables)
    # indentation_offset handles the case where the base_brick is not displayed
    if root_type == brick.thesis:
        brick.indentation_class = "ml{}".format(max([0, current_level - 1 - indentation_offset]))
    else:
        brick.indentation_class = "ml{}".format(current_level - indentation_offset)

    print(brick, current_level, rp_level, indentation_offset, brick.indentation_class)

    # set the template
    brick.template = "sober/{}".format(template_mapping.get(brick.type))

    set_title_tag(brick)

    # now apply this function recursively to all child-bricks
    res = [brick]
    processed_bricks[brick.pk] = brick
    direct_children = brick.children.all().order_by(*brick_ordering)

    for i, b in enumerate(direct_children):
        res.extend(process_child_bricks(b, root_type, rp_level,
                                        current_level + 1, max_level,
                                        indentation_offset))

    return res


def set_title_tag(brick):
    """
    determine the title tag (something like pro#3⚡2⚡1?3) and the parent_type_list

    :param brick:
    :return: None (changes brick object)
    """

    if brick.parent is None:
        assert brick.type == Brick.thesis
        # other types must have a parent (!! what is with question?)

        brick.parent_type_list = [(Brick.types_map[brick.type]+"#", brick.pk, brick.pk)]
        # this is a list which stores tuples (split_symbol, xxx, pk) for each parent
        # xxx is pk for thesis and typed_idx for other brick_types

    else:
        assert brick.parent is not None

        # this is needed, when we start with a child
        if not hasattr(brick.parent, "title_tag"):
            set_title_tag(brick.parent)

        assert hasattr(brick.parent, "parent_type_list")

        # if brick was the root
        if brick_attr_store.get((brick.pk, "typed_idx")) is None:
            brick_attr_store[(brick.pk, "typed_idx")] = 1

        new_tuple = (symbol_mapping[brick.type], brick_attr_store[(brick.pk, "typed_idx")], brick.pk)
        brick.parent_type_list = brick.parent.parent_type_list + [new_tuple]

        brick.title_tag = create_title_tag(brick.parent_type_list)

    brick.title_tag = create_title_tag(brick.parent_type_list)
    return None


def create_title_tag(parent_type_list):
    res = ""
    for symb, tidx, pk in parent_type_list:
        res += "{}{}".format(symb, tidx)

    return res


def get_root_parent(brick):
    """
    Go upward in child-parent-hierarchy and return that parent-...-parent brick which
    has no parent itself. Also return the number of upward-steps.

    :param brick:
    :return:
    """

    level = 0
    while brick.parent is not None:
        brick = brick.parent
        level += 1

    assert brick.parent is None
    return brick, level


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
