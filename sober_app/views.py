import collections
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import LANGUAGE_SESSION_KEY

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

# tmp solution until we have real internationalization
global_lc = "en"

assert len(symbol_mapping) == len(Brick.type_names_codes)


# empty object to store some attributes at runtime
class Container(object):
    pass


def view_index(request):

    # get a list of all thesis-bricks

    thesis_list = Brick.objects.filter(type=Brick.thesis)

    base_object = Container()
    base_object.page_options = Container()
    base_object.page_options.page_type = "list_of_theses"
    base_object.page_options.special_head_link = "new_thesis_link"
    # !! hcl
    base_object.page_options.title = "List of Theses"

    for tbrick in thesis_list:
        # trigger processing of the root of the respective trees (sufficient for the index)
        BrickTree(tbrick, max_alevel=0)

    base_object.sorted_child_list = thesis_list

    # list of theses -> we can savely hardcode the bb_alevel to 0
    base_object.page_options.bb_alevel = 0
    return render(request, 'sober/main_brick_tree.html', {'base': base_object})


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

    base_brick.page_options = Container()
    base_brick.page_options.page_type = "brick_detail"

    bt = BrickTree(base_brick)  # process the complete tree
    base_brick.sorted_child_list = bt.get_processed_subtree_as_list(base_brick)
    base_brick.page_options.bb_alevel = base_brick.absolute_level
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

    # sp = simple page
    sp = Container()
    sp.page_options = Container()
    sp.page_options.title = "New {1}-Brick to {0}".format(brick_id, type_code)

    sp.long_brick_type = lang[global_lc]['long_brick_type'][type_code]

    if type_code == Brick.reverse_typecode_map[Brick.thesis]:
        # ensure that we come from the correct url-dispatcher
        assert brick_id == -1
        sp.parent_brick = None
        bt = None
        sp.page_options.bb_alevel = 0

    else:
        parent_brick = get_object_or_404(Brick, pk=brick_id)
        bt = BrickTree(entry_brick=parent_brick, max_rlevel=1)

        # use the processed version of base_brick
        sp.parent_brick = bt.get_processed_subtree_as_list(base_brick=parent_brick, max_rlevel=0)[0]
        sp.page_options.bb_alevel = sp.parent_brick.absolute_level

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

            if sp.parent_brick:
                # new generation of the tree because the number of childs has changed

                bt = BrickTree(entry_brick=sp.parent_brick, max_rlevel=1)
                parent, child = bt.get_processed_subtree_as_list(sp.parent_brick,
                                                                 max_rlevel=1,
                                                                 child_filter=[new_brick.pk])
                # bb_alevel has not changed, no need to reassign
            else:
                parent = None
                bt = BrickTree(entry_brick=new_brick, max_rlevel=1)
                child = bt.get_processed_subtree_as_list(base_brick=new_brick, max_rlevel=0)[0]
                sp.page_options.bb_alevel = child.absolute_level

            sp.parent_brick, sp.newly_fabricated_brick = parent, child
            sp.utc_comment = "utc_form_successfully_processed"
            sp.content = "no errors. Form saved. Result: {}".format(new_brick)

    # here we handle the generation of an empty form
    else:
        brickform = forms.BrickForm()
        sp.content = ""
        sp.form = brickform

    if hasattr(sp, "form"):

        if type_code == Brick.reverse_typecode_map[Brick.thesis]:
            sp.form.action_url_name = "new_thesis"
        else:
            sp.form.action_url_name = "new_brick"

    context = {"pagetype": "New-Brick-Form", "sp": sp, "brick_id": brick_id, "type_code": type_code}
    return render(request, 'sober/main_simple_page.html', context)


def view_edit_brick(request, brick_id=None):
    sp = Container()
    sp.page_options = Container()
    sp.page_options.bb_alevel = 0  # on this page we only show one brick

    sp.brick_to_edit = get_object_or_404(Brick, pk=brick_id)

    type_code = Brick.reverse_typecode_map[sp.brick_to_edit.type]
    sp.long_brick_type = lang[global_lc]['long_brick_type'][type_code]
    sp.page_options.title = "Edit {1}-Brick with {0}".format(brick_id, sp.long_brick_type)

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

            bt = BrickTree(entry_brick=edited_brick, max_rlevel=0)

            sp.newly_fabricated_brick = bt.get_processed_subtree_as_list(base_brick=edited_brick,
                                                                         max_rlevel=0)[0]

            sp.utc_comment = "utc_form_successfully_processed"
            sp.content = "no errors. Form saved. Result: {}".format(edited_brick)

    # here we handle the generation of an empty form
    else:
        brickform = forms.BrickForm(instance=sp.brick_to_edit)
        sp.content = ""
        sp.form = brickform

    if hasattr(sp, "form"):
        # sp.form.form_type = "edit"
        sp.form.action_url_name = "edit_brick"

    context = {"pagetype": "Brick-Edit-Form", "sp": sp, "brick_id": brick_id, "type_code": None}
    return render(request, 'sober/main_simple_page.html', context)

    pass


def view_settings_dialog(request):

    sn = request.session
    lang = sn.get(LANGUAGE_SESSION_KEY)

    settings_counter = sn.get("settings_counter", 0)

    print("lang", lang)
    print("settings_counter", settings_counter)

    sn["settings_counter"] = settings_counter + 1

    sp = Container()
    sp.content = "This page has been visited {} times by you before.".format(settings_counter)

    context = {"pagetype": "Brick-Edit-Form", "sp": sp}
    return render(request, 'sober/main_simple_page.html', context)

# ------------------------------------------------------------------------
# below are auxiliary functions and classes which do not directly produce a view
# ------------------------------------------------------------------------


class BrickTree(object):
    """
    class representing a complete discussion
    """

    def __init__(self, entry_brick, max_alevel=float("inf"), max_rlevel=None):

        self.entry_brick = entry_brick
        self.id1 = id(entry_brick)
        self.root_parent, rp_level = get_root_parent(entry_brick)

        if max_rlevel is not None:
            max_alevel = rp_level + max_rlevel

        self.processed_bricks = collections.OrderedDict()

        # this ensures (together with line #** below) that the entry_brick instance which was
        # passed to the constructor is actually a processed one
        self.processed_bricks[entry_brick.pk] = entry_brick
        self.id2 = id(entry_brick)

        self._process_all_childs(self.root_parent, current_alevel=0, max_alevel=max_alevel)

    def _process_all_childs(self, brick, current_alevel, max_alevel=float("inf")):
        """
        for every node set the following attributes:
         - absolute_level
         - template
         - title_tag
         - parent_type_list

        :return:   None
        """

        if current_alevel > max_alevel:
            return

        # if we already touched/processed the brick then we take the respective object from our
        # local store and not from database
        # this causes 1. to use the correct instance of the entry_brick and 2. not to loose
        # the typed_index

        brick = self.processed_bricks.get(brick.pk, brick)
        self.processed_bricks[brick.pk] = brick

        brick.type_code = Brick.reverse_typecode_map[brick.type]
        brick.long_brick_type = lang[global_lc]['long_brick_type'][brick.type_code]

        brick.absolute_level = current_alevel

        type_counter = collections.Counter()
        # iterate over all children to fix their chronological order (see use of typed_idx below)
        for child in brick.children.all().order_by(*brick_ordering_chrono):

            # check if the child has been seen before
            # (use-case insertion of the concrete entry_brick instance in self.processed_bricks)
            p_child = self.processed_bricks.get(child.pk)
            if p_child is not None:
                p_child.parent = child.parent

                child = p_child
            else:
                self.processed_bricks[child.pk] = child

            type_counter.update([child.type])

            # dertermine that this child is e.g. the 3rd pro-brick on the current level
            child.typed_idx = type_counter[child.type]

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

        for i, child in enumerate(brick.direct_children):
            self._process_all_childs(brick=child, current_alevel=current_alevel + 1, max_alevel=max_alevel)

    # noinspection PyMethodMayBeStatic
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
            assert hasattr(brick, "typed_idx")

            new_tuple = ( symbol_mapping[brick.type], brick.typed_idx, brick.pk )

            brick.parent_type_list = brick.parent.parent_type_list + [new_tuple]

        brick.title_tag = create_title_tag(brick.parent_type_list)

    def get_processed_subtree_as_list(self, base_brick, max_alevel=float("inf"),
                                      max_rlevel=None, child_filter=None):
        """
        return a render-ready list of bricks

        :param base_brick:
        :param max_alevel:          int or float; maximum absolute level,
                                    default: inf; 0 -> only the base_brick
        :param max_rlevel:          None or int. if not None, then ignore parameter max_alevel
                                    and recalc max_alevel = base_brick.absolute_level + max_rlevel
        :param child_filter:        list of child_pk's which to include or None (include all)

        :return:
        """

        assert base_brick is self.processed_bricks[base_brick.pk]

        if max_rlevel is not None:
            max_alevel = base_brick.absolute_level + max_rlevel

        def tree_expand_depth_first(entry_brick, max_alevel):
            entry_brick = self.processed_bricks[entry_brick.pk]

            alevel = getattr(entry_brick, "absolute_level", None)
            if (alevel is None) or (alevel > max_alevel):
                return []

            res = [entry_brick]
            for child in entry_brick.direct_children:
                res.extend(tree_expand_depth_first(entry_brick=child, max_alevel=max_alevel))
            return res

        bricks_to_return = tree_expand_depth_first(base_brick, max_alevel=max_alevel)

        if child_filter is None:
            filter_ids = None
        else:
            filter_ids = [base_brick.pk] + child_filter

        final_bricks = []
        for brick in bricks_to_return:
            brick = self.processed_bricks[brick.pk]

            assert brick.absolute_level is not None
            assert base_brick.absolute_level is not None

            brick.relative_level = brick.absolute_level - base_brick.absolute_level
            if base_brick.type == Brick.thesis:
                brick.indentation_class = "ml{}".format(max([0, brick.relative_level - 1]))
            else:
                brick.indentation_class = "ml{}".format(brick.relative_level)

            if (filter_ids is None) or brick.pk in filter_ids:
                final_bricks.append(brick)

        return final_bricks

    def get_processed_brick(self, brick):
        return self.processed_bricks[brick.pk]


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
