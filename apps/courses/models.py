from django_prose_editor.fields import ProseEditorField
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Course(models.Model):

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="courses",
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.TextField()
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
    )

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class CourseModule(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "order"],
                name="unique_module_order_per_course",
            )
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        related_name="lessons",
    )

    title = models.CharField(max_length=200)

    slug = models.SlugField(max_length=220)

    
    content = ProseEditorField(
        extensions={
            "Bold": True,
            "Italic": True,
            "Underline": True,
            "Heading": {"levels": [2, 3, 4]},
            "BulletList": True,
            "OrderedList": True,
            "ListItem": True,
            "Link": True,
            "Code": True,
            "CodeBlock": True,
            "Blockquote": True,
            "Table": True,
            "TableRow": True,
            "TableHeader": True,
            "TableCell": True,
        },
        sanitize=True,
    )


    order = models.PositiveIntegerField(default=1)

    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "order"],
                name="unique_lesson_order_per_module",
            ),
            models.UniqueConstraint(
                fields=["module", "slug"],
                name="unique_lesson_slug_per_module",
            ),
        ]

    def __str__(self):
        return self.title
