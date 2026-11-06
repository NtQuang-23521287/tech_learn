
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.courses.models import Course, Lesson
from .models import Enrollment, LessonProgress


@require_POST
@login_required
def enroll_course(request, slug):
    course = get_object_or_404(
        Course,
        slug=slug,
        is_published=True,
    )

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
    )

    if created:
        messages.success(
            request,
            "Bạn đã đăng ký khóa học thành công!"
        )
    else:
        messages.info(
            request,
            "Bạn đã tham gia khóa học này trước đó."
        )

    return redirect(
        "courses:detail",
        slug=course.slug,
    )


@ login_required
@ require_POST
def complete_lesson(request, course_slug, module_id, lesson_slug):
    # Chỉ chấp nhận bài học và khóa học đã xuất bản.
    lesson = get_object_or_404(
        Lesson,
        slug=lesson_slug,
        module_id=module_id,
        module__course__slug=course_slug,
        module__course__is_published=True,
        is_published=True,
    )

    # Học viên phải tham gia đúng khóa học.
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=lesson.module.course,
    )

    # Không tạo bản ghi trùng khi nhấn nhiều lần.
    progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
    )

    if created:
        messages.success(
            request,
            "Chúc mừng! Bạn đã hoàn thành bài học."
        )
    else:
        messages.info(
            request,
            "Bạn đã hoàn thành bài học này trước đó."
        )

    return redirect(
        "courses:lesson_detail",
        course_slug=course_slug,
        module_id=module_id,
        lesson_slug=lesson_slug,
    )
