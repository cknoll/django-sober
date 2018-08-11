from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Brick


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

    base_brick.sorted_child_list = [base_brick]

    return render(request, 'sober/main_brick_tree.html', {'brick': base_brick})

