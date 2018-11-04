"""
This module contains classes and functions which extend various models.

Because this functionality is view-specific it is separated from the bare models.
"""

import collections

from django.utils.translation import gettext_lazy as _

from .models import Brick, Vote
from .forms import forms
from .language import lang

from ipydex import IPS

# tmp solution until we have real internationalization
# !! this is ugly and can be removed after elimination of langugage.py
global_lc = "en"


brick_ordering = ['type', 'cached_avg_vote', 'update_datetime']
brick_ordering_chrono = ['type', 'creation_datetime']

template_mapping = {Brick.thesis: "brick_thesis.html",
                    Brick.pro: "brick_pro.html",
                    Brick.contra: "brick_contra.html",
                    Brick.question: "brick_question.html",
                    Brick.comment: "brick_comment.html",
                    Brick.improvement: "brick_improvement.html",
                    # !! todo own template
                    }


class BrickTree(object):
    """
    class representing a complete discussion
    """

    def __init__(self, entry_brick, max_alevel=float("inf"), max_rlevel=None):
        """

        :param entry_brick:
        :param max_alevel:      max. absolute level
        :param max_rlevel:      max. relative level
        """

        self.entry_brick = entry_brick
        self.id1 = id(entry_brick)
        self.root_parent, rp_level = entry_brick.get_root_parent()

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
        brick.current_tree_parent = self.entry_brick
        brick.vote_form = forms.VoteForm(instance=Vote())

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

        list_map = self._prepare_child_type_lists(brick)

        for i, child in enumerate(brick.direct_children):
            # add the child to the respective list
            list_map[child.type].append(child)

            self._process_all_childs(brick=child, current_alevel=current_alevel + 1, max_alevel=max_alevel)

    @staticmethod
    def _prepare_child_type_lists(brick):
        """
        Prepare data structures and return a dict, for quick access to these lists
        via <child>.type
        :param brick:

        :return: list_map
        """
        # allow access to specific types of childrens
        brick.direct_children_pro = []
        brick.direct_children_contra = []
        brick.direct_children_rest = []

        def default_factory():
            return brick.direct_children_rest
        list_map = collections.defaultdict(default_factory)
        list_map[Brick.pro] = brick.direct_children_pro
        list_map[Brick.contra] = brick.direct_children_contra

        return list_map

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

            ptype = _("Thesis")

            brick.parent_type_list = [(ptype + "#", brick.pk, brick.pk)]
            # this is a list which stores tuples (split_symbol, xxx, pk) for each parent
            # xxx is pk for thesis and typed_idx for other brick_types

        else:
            assert hasattr(brick.parent, "title_tag")
            assert hasattr(brick.parent, "parent_type_list")
            assert hasattr(brick, "typed_idx")

            new_tuple = (Brick.symbol_mapping[brick.type], brick.typed_idx, brick.pk )

            brick.parent_type_list = brick.parent.parent_type_list + [new_tuple]

        brick.title_tag = create_title_tag(brick.parent_type_list)

    def get_processed_subtree_as_list(self, base_brick, max_alevel=float("inf"),
                                      max_rlevel=None, included_childs="__all__"):
        """
        return a render-ready list of bricks.
            1. Get the bricks in the right order
            2. Tweak the brick with context-dependet information (indendation class, etc)

        :param base_brick:
        :param max_alevel:          int or float; maximum absolute level,
                                    default: inf; 0 -> only the base_brick
        :param max_rlevel:          None or int. if not None, then ignore parameter max_alevel
                                    and recalc max_alevel = base_brick.absolute_level + max_rlevel
        :param included_childs:     list of child_pk's which to include or "__all__" (include all)

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

        if included_childs is "__all__":
            included_ids = "__all__"
        else:
            included_ids = [base_brick.pk] + included_childs

        # processing of the bricks has two-stages
        # here the final tweaking of the brick takes place
        final_bricks = []
        for brick in bricks_to_return:
            if (included_ids != "__all__") and (brick.pk not in included_ids):
                continue

            brick = self.processed_bricks[brick.pk]

            assert brick.absolute_level is not None
            assert base_brick.absolute_level is not None

            brick.relative_level = brick.absolute_level - base_brick.absolute_level
            if base_brick.type == Brick.thesis:
                brick.indentation_class = "ml{}".format(max([0, brick.relative_level - 1]))
            else:
                brick.indentation_class = "ml{}".format(brick.relative_level)

            final_bricks.append(brick)

        return final_bricks

    def get_processed_brick(self, brick):
        return self.processed_bricks[brick.pk]


def create_title_tag(parent_type_list):
    res = ""
    for symb, tidx, pk in parent_type_list:
        res += "{}{}".format(symb, tidx)

    return res
