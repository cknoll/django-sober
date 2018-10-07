from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_index, name='index'),
    path('thesis-list', views.view_thesis_list, name='thesis_list'),
    path('b/<int:brick_id>', views.view_renderbrick, name='show_brick'),
    path('b/<int:brick_id>/edit', views.view_edit_brick, name='edit_brick'),
    path('b/new_thesis', views.view_new_brick, name='new_thesis',
         kwargs={"brick_id": -1, "type_code": "th"}),
    path('b/<int:brick_id>/<str:type_code>', views.view_new_brick, name='new_brick'),
    path('settings', views.view_settings_dialog, name='settings_dialog'),
    path('debug', views.view_debug, name='debug_page'),
    path('debug/<str:optionstr>', views.view_debug, name='debug_page'),
    path('<str:pagetype>', views.view_simple_page, name='simplepage'),
]
