
from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    path(
        "history/",
        views.quiz_history,
        name="history",
    ),

    # Trang lịch sử của một Quiz
    path(
        "<int:quiz_id>/",
        views.quiz_overview,
        name="detail",
    ),

    # Trang làm Quiz
    path(
        "<int:quiz_id>/take/",
        views.quiz_detail,
        name="take",
    ),

    # Xử lý nộp bài
    path(
        "<int:quiz_id>/submit/",
        views.submit_quiz,
        name="submit",
    ),

    # Xem kết quả một lần làm
    path(
        "attempts/<int:attempt_id>/",
        views.quiz_result,
        name="result",
    ),
]
