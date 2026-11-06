
from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list, name="list"),

    path(
        "<slug:course_slug>/modules/<int:module_id>/lessons/<slug:lesson_slug>/",
        views.lesson_detail,
        name="lesson_detail",
    ),

    path("<slug:slug>/", views.course_detail, name="detail"),
]
