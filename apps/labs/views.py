
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from apps.progress.models import Enrollment

from .models import Lab, LabTask


@login_required
@require_GET
def lab_detail(request, lab_id):

    lab = get_object_or_404(
        Lab.objects.select_related(
            "lesson__module__course"
        ).prefetch_related(
            Prefetch(
                "tasks",
                queryset=LabTask.objects.only(
                    "id",
                    "lab_id",
                    "title",
                    "instructions",
                    "order",
                ),
            )
        ),
        pk=lab_id,
    )

    lesson = lab.lesson
    course = lesson.module.course

    # Quản trị viên được xem trước Lab bản nháp.
    if not request.user.is_staff:

        if not (
            lab.is_published
            and lesson.is_published
            and course.is_published
        ):
            raise Http404(
                "Lab chưa được xuất bản."
            )

        # Chỉ học viên đã đăng ký khóa học được xem.
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
        ).exists()

        if not is_enrolled:
            raise Http404(
                "Bạn chưa tham gia khóa học."
            )

    return render(
        request,
        "labs/lab_detail.html",
        {
            "lab": lab,
            "lesson": lesson,
            "course": course,
            "tasks": lab.tasks.all(),
        },
    )
