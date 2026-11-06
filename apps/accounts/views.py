from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import StudentRegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect("courses:list")
    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )