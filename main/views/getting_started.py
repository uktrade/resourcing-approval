from django.shortcuts import render


def getting_started(request):
    return render(request, "main/getting_started.html")
