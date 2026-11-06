
from django.urls import path

from . import views


app_name = "progress"

urlpatterns = [
    path(
        "enroll/<slug:slug>/",
        views.enroll_course,
        name="enroll",
    ),

    path(
        "complete/<slug:course_slug>/<int:module_id>/<slug:lesson_slug>/",
        views.complete_lesson,
        name="complete_lesson",
    ),
]
