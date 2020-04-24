from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .models import PPEType

urlpatterns = [
    path("", views.index_view, name="index_view"),
    path("home/", views.home_view, name="home_view"),
    path("home/inventory/", views.inventory_list_view, name="inventory_list_view"),
    path("home/onboard/", views.onboard_view, name="onboard_view"),
    path(
        "home/onboard/connect/", views.onboard_connect_view, name="onboard_connect_view"
    ),
    path(
        "home/onboard/new-provider/",
        views.onboard_new_provider_view,
        name="onboard_new_provider_view",
    ),
    path(
        "home/onboard/new-parent/",
        views.onboard_new_parent_view,
        name="onboard_new_parent_view",
    ),
    path("register/", views.register_view, name="register_view",),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password-reset/confirm/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "track/n95-masks/",
        views.TrackInventoryView.as_view(ppe_type=PPEType.N95MASK),
        name="track_mask_view",
    ),
    path(
        "track/gloves/",
        views.TrackInventoryView.as_view(ppe_type=PPEType.GLOVES),
        name="track_glove_view",
    ),
    path(
        "track/alcohol/",
        views.TrackInventoryView.as_view(ppe_type=PPEType.ALCOHOL),
        name="track_alcohol_view",
    ),
    path(
        "track/swab/",
        views.TrackInventoryView.as_view(ppe_type=PPEType.SWAB),
        name="track_swab_view",
    ),
    path(
        "track/gowns/",
        views.TrackInventoryView.as_view(ppe_type=PPEType.GOWNS),
        name="track_gowns_view",
    ),
    path(
        "track/face-mask/",
        views.TrackInventoryView.as_view(ppe_type=PPEType.FACE_MASK),
        name="track_face_mask_view",
    ),
    path("dashboard/", views.dashboard_view, name="dashboard_view"),
    path(
        "dashboard/download",
        views.download_dashboard_view,
        name="download_dashboard_view",
    ),
]
