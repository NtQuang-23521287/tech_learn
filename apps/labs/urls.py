
from django.urls import path

from . import views


app_name = "labs"

urlpatterns = [
    path(
        "<int:lab_id>/",
        views.lab_detail,
        name="detail",
    ),
]
