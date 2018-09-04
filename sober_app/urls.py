from django.urls import path

from . import views

urlpatterns = [
    path('', views.view_index, name='index'),
    path('b/<int:brick_id>', views.view_renderbrick, name='brickid'),
    path('b/<int:brick_id>/edit', views.view_edit_brick, name='edit_brick'),
    path('b/new_thesis', views.view_new_brick, name='new_thesis', kwargs={"brick_id": -1, "type_code": "th"}),
    path('b/<int:brick_id>/<str:type_code>', views.view_new_brick, name='new_brick'),
    path('<str:pagetype>', views.view_simple_page, name='simplepage'),
]
