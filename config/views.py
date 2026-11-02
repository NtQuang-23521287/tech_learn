from django.http import HttpResponse

def home(request):
    return HttpResponse(
        "<h1>Welcome to TechLearn!</h1>"
        "<p>Learn Linux, Networking & System Administration</p>"
    )