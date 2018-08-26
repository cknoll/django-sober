from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('b/<int:brick_id>', views.renderbrick_l0, name='brickid'),
    path('<str:pagetype>', views.simple_page, name='simplepage'),
]
