
from django.shortcuts import render


def home(request):
    context = {
        "page_title": "TechLearn",
        "welcome_message": "Learn IT. Practice IT.",
    }

    return render(
        request,
        "core/home.html",
        context,
    )
