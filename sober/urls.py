from django.urls import path
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path("", views.view_index, name="index"),
    path("thesis-list", views.view_thesis_list, name="thesis_list"),
    path("b/<int:tree_base_brick_id>", views.ViewRenderBrick.as_view(), name="show_brick"),
    path("b/<int:brick_id>/edit", views.view_edit_brick, name="edit_brick"),
    path(
        "b/new_thesis",
        views.ViewNewBrick.as_view(),
        name="new_thesis",
        kwargs={"brick_id": -1, "type_code": "th"},
    ),
    path("b/<int:brick_id>/<str:type_code>", views.ViewNewBrick.as_view(), name="new_brick"),
    path("settings", views.view_settings_dialog, name="settings_dialog"),
    path("feedback", views.ViewFeedback.as_view(), name="feedback_page"),
    path("group/<int:group_id>", views.view_group_details, name="group_details"),
    path("accounts/login/", views.ViewAdaptedLogin.as_view(), name="login_page"),
    path("accounts/logout/", views.view_logout, name="logout_page"),
    path("accounts/profile/", views.view_profile, name="profile_page"),
    path("accounts/register/", views.view_register, name="register_page"),
    path("export/<str:arg>", views.view_export, name="export_page"),  # export a brick as raw_json
    path("debug", views.view_debug, name="debug_page"),
    path("debug_mail", views.view_debug_mail, name="debug_mail_page"),
    path("debug_login", views.view_debug_login, name="debug_login_page"),
    path("debug/<str:optionstr>", views.view_debug, name="debug_page"),
    path("md-preview/<int:url_id>", views.ViewMdPreview.as_view(), name="md_preview"),
    path("md-preview/<str:strarg>", views.ViewMdPreview.as_view(), name="md_preview"),
    path("imprint", views.view_simple_page, name="imprint-page", kwargs={"pagetype": "imprint"}),
    path("privacy", views.view_simple_page, name="privacy-page", kwargs={"pagetype": "privacy"}),
    path("contact", views.view_simple_page, name="contact-page", kwargs={"pagetype": "contact"}),
    path(
        "__inzn_test",
        views.view_simple_page,
        name="international_test",
        kwargs={"pagetype": "__inzn_test"},
    ),
    path("<str:pagetype>", views.view_simple_page, name="simplepage"),
]
